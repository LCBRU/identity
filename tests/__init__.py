from unittest.mock import patch
from lbrc_flask.database import db
from identity.security import login_user, init_users
from identity.model import Study


def login(client, faker):
    init_users()

    u = faker.user_details()
    db.session.add(u)
    db.session.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = u.id
        sess['_fresh'] = True # https://flask-login.readthedocs.org/en/latest/#fresh-logins
    
    # Some stuff is created on first request, so do that
    client.get("/")

    # Login for access to functions directly
    login_user(u)

    # Login for access by flask client
    with patch('identity.model.security.ldap') as mock:
        client.post('/login', data=dict(
            username=u.username,
            password='a little bit further'
        ), follow_redirects=True)

    return u


def add_all_studies(user):
    user.studies.update(Study.query.all())


def flash_messages_contains_error(client):
    with client.session_transaction() as session:
        return dict(session['_flashes']).get('error') is not None
