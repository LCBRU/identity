from datetime import datetime
from celery.schedules import crontab
from flask import current_app
from sqlalchemy.sql import text
from identity.celery import celery
from identity.database import redcap_engine, db
from identity.model import RedcapInstance, RedcapProject
from identity.security import get_system_user

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
