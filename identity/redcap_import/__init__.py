from dateutil.parser import parse
from datetime import datetime
from celery.schedules import crontab
from flask import current_app
from sqlalchemy.sql import text
from sqlalchemy import func
from identity.celery import celery
from identity.database import redcap_engine, db
from identity.model import RedcapInstance, RedcapProject, EcrfDetail
from identity.security import get_system_user
from identity.redcap_import.model import BriccsImportStrategy


def init_redcap_import(app):
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
        import_new_participants.s(),
    )


@celery.task
def import_project_details():
    current_app.logger.info('Importing REDCap projects')

    system_user = get_system_user()

    for r in RedcapInstance.query.all():

        with redcap_engine(r.database_name) as conn:
            current_app.logger.info(f'importing projects from REDCap instance: {r.name}')

            for p in conn.execute(text("""
                SELECT
                    project_id,
                    app_title
                FROM redcap_projects
                """)):

                rp = RedcapProject.query.filter_by(project_id=p['project_id'], redcap_instance_id=r.id).one_or_none()

                if rp is None:
                    current_app.logger.info(f'Adding project \'{p["app_title"]}\' for instance \'{r.name}\' ')

                    rp = RedcapProject(
                        name=p['app_title'],
                        project_id=p['project_id'],
                        redcap_instance=r,
                        last_updated_by_user=system_user,
                    )
                    db.session.add(rp)
                elif rp.name != p['app_title']:
                    current_app.logger.info(f'Updating project \'{p["app_title"]}\' for instance \'{r.name}\' ')

                    rp.name = p['app_title']
                    rp.last_updated_by_user = system_user
                    rp.last_updated_datetime = datetime.utcnow()
                    db.session.add(rp)

    db.session.commit()


@celery.task
def import_new_participants():
    current_app.logger.info('Importing REDCap particiapnts')

    system_user = get_system_user()

    for r in RedcapInstance.query.all()[0:1]:
        strategy = BriccsImportStrategy()
        
        with redcap_engine(r.database_name) as conn:
            current_app.logger.info(f'importing participants from REDCap instance: {r.name}')

            max_timestamp, = db.session.query(func.max(EcrfDetail.ecrf_timestamp)).one()

            current_app.logger.info(f'Previous timestamp: {max_timestamp}')

            for p in conn.execute(
                text(strategy.get_query()),
                timestamp=max_timestamp or 0,
                project_id=24,
            ):

                ecrf = strategy.fill_ecrf(
                    p,
                    EcrfDetail.query.filter_by(
                        project_id=p['project_id'],
                        ecrf_participant_identifier=p['record']
                    ).one_or_none(),
                )

                ecrf.ecrf_timestamp=p['last_update_timestamp']
                ecrf.last_updated_by_user_id=system_user.id
                ecrf.last_updated_datetime=datetime.utcnow()

                strategy.fill_identifiers(p, ecrf, system_user)

                db.session.add_all(ecrf.identifiers)
                db.session.add(ecrf)

            db.session.commit()

    current_app.logger.info('Importing REDCap particiapnts - Done')
