import urllib
from identity.database import db
from identity.model.security import User
from identity.api.model import ApiKey


def get_api_key(faker):
    u = faker.user_details()
    db.session.add(u)

    a = ApiKey()
    a.user = u
    db.session.add(a)

    db.session.commit()

    return a


def add_parameters_to_url(url, parameters):
    url_parts = urllib.parse.urlparse(url)
    q = urllib.parse.parse_qs(url_parts.query)
    q.update(parameters)
    url_parts = url_parts._replace(query = urllib.parse.urlencode(q))

    return urllib.parse.urlunparse(url_parts)


def add_api_key_to_url(faker, url):
    api_key = get_api_key(faker)

    return add_parameters_to_url(url, {'api_key': api_key.key})
