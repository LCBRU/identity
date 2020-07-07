from itertools import chain
from dateutil.parser import parse
from datetime import datetime
from celery.schedules import crontab
from flask import current_app
from sqlalchemy.sql import text
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from identity.celery import celery
from identity.database import redcap_engine, db
from identity.redcap.model import (
    RedcapInstance,
    RedcapProject,
    EcrfDetail,
)
from identity.model.id import (
    ParticipantIdentifierType,
    ParticipantIdentifier,
)
from identity.security import get_system_user
from identity.utils import log_exception


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


@celery.task
def import_project_details():
    current_app.logger.info('Importing REDCap projects')

    for instance in RedcapInstance.query.all():
        try:    
            _load_instance_projects(instance)
        except Exception as e:
            log_exception(e)

    db.session.commit()

    current_app.logger.info('Importing REDCap projects - COMPLETED')


def _load_instance_projects(instance):

    system_user = get_system_user()

    with redcap_engine(instance.database_name) as conn:
        current_app.logger.info(f'importing projects from REDCap instance: {instance.name}')

        for p in conn.execute(text("""
            SELECT
                project_id,
                app_title
            FROM redcap_projects
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


@celery.task
def import_participants():

    current_app.logger.info('Importing REDCap particiapnts')

    system_user = get_system_user()

    for p in RedcapProject.query.filter(RedcapProject.study_id != None, RedcapProject.participant_import_definition_id != None).all():
        try:
            _load_participants(p, system_user)
        except Exception as e:
            log_exception(e)
    
    db.session.commit()

    current_app.logger.info('Importing REDCap particiapnts - Done')


def _load_participants(project, system_user):
    current_app.logger.info(f'_load_instance_participants: project="{project.name}"')

    max_timestamp, = db.session.query(func.max(EcrfDetail.ecrf_timestamp)).filter_by(redcap_project_id=project.id).one()
    current_app.logger.info(f'Project {project.name} previous timestamp: {max_timestamp}')

    with redcap_engine(project.redcap_instance.database_name) as conn:
        type_ids = {pt.name: pt.id for pt in ParticipantIdentifierType.query.all()}    
        ecrfs = []
        all_ids = {}

        participants = conn.execute(
            text(project.participant_import_definition.get_query()),
            timestamp=max_timestamp or 0,
            project_id=project.project_id,
        )

        rows = 0

        for participant in participants:
            rows += 0

            ecrf = project.participant_import_definition.fill_ecrf(
                redcap_project=project,
                participant_details=participant,
                existing_ecrf=EcrfDetail.query.filter_by(
                    redcap_project_id=project.id,
                    ecrf_participant_identifier=participant['record']
                ).one_or_none(),
            )

            ecrf.ecrf_timestamp=participant['last_update_timestamp']
            ecrf.last_updated_by_user_id=system_user.id
            ecrf.last_updated_datetime=datetime.utcnow()

            ecrf.identifier_source.last_updated_by_user_id=system_user.id
            ecrf.identifier_source.last_updated_datetime=datetime.utcnow()

            add_identifiers(ecrf, project, all_ids, participant, type_ids, system_user)
            
            ecrfs.append(ecrf)
            
        db.session.add_all(ecrfs)

    current_app.logger.info(f'_load_instance_participants: project="{project.name}" imported {rows} records')


def add_identifiers(ecrf, project, all_ids, participant, type_ids, system_user):

    ecrf.identifier_source.identifiers.clear()

    for id in project.participant_import_definition.extract_identifiers(participant):

        idkey = frozenset(id.items())

        if idkey in all_ids:
            i = all_ids[idkey]
        else:
            i = ParticipantIdentifier.query.filter_by(
                participant_identifier_type_id=type_ids[id['type']],
                identifier=id['identifier'],
            ).one_or_none()

            if i is None:
                i = ParticipantIdentifier(
                    participant_identifier_type_id=type_ids[id['type']],
                    identifier=id['identifier'],
                    last_updated_by_user_id=system_user.id,
                )
            
            all_ids[idkey] = i
        
        ecrf.identifier_source.identifiers.add(i)
