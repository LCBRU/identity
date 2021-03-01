from lbrc_flask.requests import add_parameters_to_url


def add_api_key_to_url(api_key, url):
    return add_parameters_to_url(url, {'api_key': api_key.key})
