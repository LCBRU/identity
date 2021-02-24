#!/usr/bin/env python3

import inspect
import traceback
from flask import current_app
from identity.emailing import email


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.
    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }
    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme

        server = environ.get('HTTP_X_FORWARDED_SERVER', '')
        if server:
            environ['HTTP_HOST'] = server

        return self.app(environ, start_response)


def log_exception(e):
    print(traceback.format_exc())
    current_app.logger.error(traceback.format_exc())
    email(
        subject=current_app.config["ERROR_EMAIL_SUBJECT"],
        message=traceback.format_exc(),
        recipients=[current_app.config["ADMIN_EMAIL_ADDRESS"]],
    )


def get_concrete_classes(cls):
    current_app.logger.info(f'get_concrete_label_packs')

    result = [sub() for sub in cls.__subclasses__()
              if len(sub.__subclasses__()) == 0 and
              # If the constructor requires parameters
              # other than self (i.e., it has more than 1
              # argument), it's an abstract class
              len(inspect.getfullargspec(sub.__init__)[0]) == 1]

    for sub in [sub for sub in cls.__subclasses__()
                if len(sub.__subclasses__()) != 0]:
        result += get_concrete_classes(sub)

    return result
