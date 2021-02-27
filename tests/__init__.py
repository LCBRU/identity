from identity.model import Study


def add_all_studies(user):
    user.studies.update(Study.query.all())


def flash_messages_contains_error(client):
    with client.session_transaction() as session:
        return dict(session['_flashes']).get('error') is not None
