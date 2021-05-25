from datetime import datetime
from celery.schedules import crontab
from flask import current_app
from sqlalchemy import select, func, and_
from sqlalchemy.sql import text
from sqlalchemy.orm import aliased
from identity.celery import celery
from identity.database import redcap_engine
from lbrc_flask.database import db
from .model import (
    ParticipantImportDefinition, RedcapInstance,
    RedcapProject,
    EcrfDetail,
)
from identity.model.id import (
    ParticipantIdentifierSource,
    ParticipantIdentifierType,
    ParticipantIdentifier,
)
from lbrc_flask.security import get_system_user
from lbrc_flask.logging import log_exception
import multiprocessing
from identity.model.id import participant_identifiers__participant_identifier_sources


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
        start = datetime.utcnow()
        current_app.logger.info('Importing REDCap particiapnts')

        p = ParticipantImporter()
        p.run()

        duration = datetime.utcnow() - start
        current_app.logger.info(f'Importing REDCap particiapnts - Done in {duration}')


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
        id_cache = {}

        for pid in ParticipantImportDefinition.query.filter(ParticipantImportDefinition.active == True).all():
            try:
                if pid.ecrf_source.has_new_data(pid.latest_timestamp):
                    self._load_participants(pid, id_cache)

                db.session.commit()

            except Exception as e:
                log_exception(e)
        
        self._merge_participants()

    def _merge_participants(self):
        current_app.logger.info(f'Merging Participants')

        pism = ParticipantIdentifierSource.__table__.alias('pism')
        pipis1 = participant_identifiers__participant_identifier_sources.alias('pipis1')
        pipis2 = participant_identifiers__participant_identifier_sources.alias('pipis2')

        j = pism\
            .join(pipis1, pipis1.c.participant_identifier_source_id == pism.c.id)\
            .join(pipis2, and_(
                pipis2.c.participant_identifier_id == pipis1.c.participant_identifier_id,
                pipis2.c.participant_identifier_source_id < pism.c.linked_minimum_patient_identifier_source_id
            ))

        q = select([pism.c.id, func.min(pipis2.c.participant_identifier_source_id)])\
            .select_from(j)\
            .group_by(pism.c.id)

        with db.engine.connect() as conn:

            while True:
                update_mappings = [{
                    'id': id,
                    'linked_minimum_patient_identifier_source_id': linked_minimum_patient_identifier_source_id
                } for id, linked_minimum_patient_identifier_source_id in conn.execute(q).fetchall()]

                if len(update_mappings) == 0:
                    break

                current_app.logger.info(f'Merge Participant Count = {len(update_mappings)}')

                db.session.bulk_update_mappings(ParticipantIdentifierSource, update_mappings)
                db.session.commit()

    def _load_participants(self, pid, id_cache):
        current_app.logger.info(f'Importing Participants: pidid="{pid.id}" study="{pid.study.name}"; source="{pid.ecrf_source.name}".')

        ecrfs = []

        for participant in pid.ecrf_source.get_participants(pid):
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

        current_app.logger.info(f'Importing Participants: study="{pid.study.name}"; redcap instance="{pid.ecrf_source.name}". Imported {len(ecrfs)} records')


    def add_identifiers(self, ecrf, pid, participant, id_cache):

        ecrf.identifier_source.identifiers.clear()

        for id in pid.extract_identifiers(participant):
            ecrf.identifier_source.identifiers.add(self.get_or_create_id(id, id_cache))

    
    def get_or_create_id(self, id, id_cache):
        identifier = id['identifier']
        id_type = id['type'].strip().lower()

        if type(identifier) == str:
            identifier = identifier.strip().lower()

        idkey = frozenset([id_type, identifier])

        if idkey in id_cache:
            i = id_cache[idkey]
        else:
            i = ParticipantIdentifier.query.filter_by(
                participant_identifier_type_id=self.id_types[id_type],
                identifier=identifier,
            ).one_or_none()

            if i is None:
                i = ParticipantIdentifier(
                    participant_identifier_type_id=self.id_types[id_type],
                    identifier=identifier,
                    last_updated_by_user_id=self.user.id,
                )
            
            id_cache[idkey] = i
        
        return i
