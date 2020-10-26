from datetime import datetime
from celery.schedules import crontab
from flask import current_app
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import text
from sqlalchemy import func
from identity.celery import celery
from identity.database import redcap_engine, db
from identity.redcap.model import (
    ParticipantImportDefinition, RedcapInstance,
    RedcapProject,
    EcrfDetail,
)
from identity.model.id import (
    ParticipantIdentifierType,
    ParticipantIdentifier,
)
from identity.security import get_system_user
from identity.utils import log_exception
import multiprocessing


def init_redcap(app):
    pass


@celery.on_after_configure.connect
def setup_import_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(
            minute=current_app.config['REDCAP_PROJECT_SCHEDULE_MINUTE'],
            hour=current_app.config['REDCAP_PROJECT_SCHEDULE_HOUR'],
        ),
        import_project_details.s(),
    )
    sender.add_periodic_task(
        crontab(
            minute=current_app.config['REDCAP_PARTICIPANTS_SCHEDULE_MINUTE'],
            hour=current_app.config['REDCAP_PARTICIPANTS_SCHEDULE_HOUR'],
        ),
        import_participants.s(),
    )


lock = multiprocessing.Lock()


@celery.task
def import_participants():
    current_app.logger.warning('REDCap participant import: waiting for lock')
    with lock:
        current_app.logger.warning('Importing REDCap particiapnts')

        p = ParticipantImporter()
        p.run()

        current_app.logger.warning('Importing REDCap particiapnts - Done')


@celery.task
def import_project_details():
    current_app.logger.warning('REDCap project import: waiting for lock')
    with lock:
        current_app.logger.info('Importing REDCap projects')

        p = ProjectImporter()
        p.run()

        current_app.logger.info('Importing REDCap projects - COMPLETED')


class ProjectImporter():
    def run(self):
        for instance in RedcapInstance.query.all():
            try:    
                self._load_instance_projects(instance)
            except Exception as e:
                log_exception(e)

        db.session.commit()

    def _load_instance_projects(self, instance):

        system_user = get_system_user()

        with redcap_engine(instance.database_name) as conn:
            current_app.logger.info(f'importing projects from REDCap instance: {instance.name}')

            for p in conn.execute(text("""
                SELECT
                    project_id,
                    app_title
                FROM redcap_projects
                WHERE date_deleted IS NULL
                    AND status = 1
                """)):

                rp = RedcapProject.query.filter_by(project_id=p['project_id'], redcap_instance_id=instance.id).one_or_none()

                if rp is None:
                    current_app.logger.info(f'Adding project \'{p["app_title"]}\' for instance \'{instance.name}\' ')

                    rp = RedcapProject(
                        name=p['app_title'],
                        project_id=p['project_id'],
                        redcap_instance=instance,
                        last_updated_by_user=system_user,
                    )
                    db.session.add(rp)
                elif rp.name != p['app_title']:
                    current_app.logger.info(f'Updating project \'{p["app_title"]}\' for instance \'{instance.name}\' ')

                    rp.name = p['app_title']
                    rp.last_updated_by_user = system_user
                    rp.last_updated_datetime = datetime.utcnow()
                    db.session.add(rp)


class ParticipantImporter():

    def __init__(self):
        self.user = get_system_user()
        self.id_types = {pt.name.lower(): pt.id for pt in ParticipantIdentifierType.query.all()}

    def run(self):
        timestamps = self.get_max_timestamps()

        for ri in RedcapInstance.query.all():
            with redcap_engine(ri.database_name) as conn:

                new_time_stamps = get_new_timestamps(conn)

                for pid in ParticipantImportDefinition.query.join(ParticipantImportDefinition.redcap_project).filter(RedcapProject.redcap_instance_id==ri.id).all():
                    try:
                        ts = timestamps.get(pid.id, 0)
                        new_ts = new_time_stamps.get(pid.redcap_project.project_id, -1)

                        if new_ts > ts:
                            current_app.logger.info(f'Existing timestamps {ts}; New timestamp {new_ts}')

                            self._load_participants(pid, conn, ts)

                        db.session.commit()

                    except Exception as e:
                        log_exception(e)


    def _load_participants(self, pid, conn, max_timestamp):
        current_app.logger.info(f'Importing Participants: pidid="{pid.id}" study="{pid.study.name}"; redcap instance="{pid.redcap_project.redcap_instance.name}"; project="{pid.redcap_project.name}".')

        ecrfs = []
        id_cache = {}

        participants = conn.execute(
            text(pid.get_query()),
            timestamp=max_timestamp,
            project_id=pid.redcap_project.project_id,
        )

        for participant in participants:
            ecrf = pid.fill_ecrf(
                participant_details=participant,
                existing_ecrf=EcrfDetail.query.filter_by(
                    participant_import_definition_id=pid.id,
                    ecrf_participant_identifier=participant['record']
                ).one_or_none(),
            )

            ecrf.ecrf_timestamp=participant['last_update_timestamp']
            ecrf.last_updated_by_user_id=self.user.id
            ecrf.last_updated_datetime=datetime.utcnow()

            ecrf.identifier_source.last_updated_by_user_id=self.user.id
            ecrf.identifier_source.last_updated_datetime=datetime.utcnow()

            self.add_identifiers(ecrf, pid, participant, id_cache)
            
            ecrfs.append(ecrf)

        db.session.add_all(ecrfs)

        current_app.logger.info(f'Importing Participants: study="{pid.study.name}"; redcap instance="{pid.redcap_project.redcap_instance.name}"; project="{pid.redcap_project.name}". Imported {len(ecrfs)} records')


    def add_identifiers(self, ecrf, pid, participant, id_cache):

        ecrf.identifier_source.identifiers.clear()

        for id in pid.extract_identifiers(participant):
            ecrf.identifier_source.identifiers.add(self.get_or_create_id(id, id_cache))

    
    def get_or_create_id(self, id, id_cache):
        idkey = frozenset(id.items())

        if idkey in id_cache:
            i = id_cache[idkey]
        else:
            i = ParticipantIdentifier.query.filter_by(
                participant_identifier_type_id=self.id_types[id['type'].lower()],
                identifier=id['identifier'],
            ).one_or_none()

            if i is None:
                i = ParticipantIdentifier(
                    participant_identifier_type_id=self.id_types[id['type'].lower()],
                    identifier=id['identifier'],
                    last_updated_by_user_id=self.user.id,
                )
            
            id_cache[idkey] = i
        
        return i
            

    def get_max_timestamps(self):
        return {x[0]: x[1] for x in db.session.query(
                EcrfDetail.participant_import_definition_id,
                func.max(EcrfDetail.ecrf_timestamp),
            ).group_by(EcrfDetail.participant_import_definition_id).all()}


def get_new_timestamps(conn):
    return {r['project_id']: r['ts'] for r in conn.execute('''
        SELECT
            project_id,
            MAX(COALESCE(ts, 0)) AS ts
        FROM redcap_log_event
        WHERE event IN ('INSERT', 'UPDATE')
            # Ignore events caused by the data import from
            # the mobile app
            AND page NOT IN ('DataImportController:index')
            AND object_type = 'redcap_data'
        GROUP BY project_id
    ''')}

