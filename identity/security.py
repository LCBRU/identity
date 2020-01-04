#!/usr/bin/env python3

import time
import ldap
import pprint
from functools import wraps
from flask import g, current_app
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    current_user,
)
from .model import User, Role
from .database import db

SYSTEM_USER_NAME = 'system'

login_manager = LoginManager()


def init_security(app):
    login_manager.init_app(app)
    login_manager.login_view = "security_ui.login"

    @app.before_request
    def get_current_user():
        g.user = current_user


def init_users():
    if not get_system_user():
        system = User(
            username=SYSTEM_USER_NAME,
            first_name='HAL',
            last_name='',
        )
        db.session.add(system)

    if not get_admin_role():
        admin = Role(
            name=Role.ADMIN_ROLENAME,
            last_updated_by_user=get_system_user(),
        )
        db.session.add(admin)

    if User.query.filter_by(username=current_app.config['ADMIN_USER_USERNAME']).count() == 0:
        admin = User(
            username=current_app.config['ADMIN_USER_USERNAME'],
            first_name=current_app.config['ADMIN_USER_FIRST_NAME'],
            last_name=current_app.config['ADMIN_USER_LAST_NAME'],
        )
        admin.roles.add(get_admin_role())
        db.session.add(admin)

    db.session.commit()


def get_system_user():
    current_app.logger.info(f'SYSTEM_USER_NAME: {SYSTEM_USER_NAME}')
    return User.query.filter_by(username=SYSTEM_USER_NAME).first()


def get_admin_user():
    return User.query.filter_by(username=current_app.config['ADMIN_USER_USERNAME']).first()


def get_admin_role():
    return Role.query.filter_by(name=Role.ADMIN_ROLENAME).first()


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


def login(username, password):
    current_app.logger.info('Username supplied for login: %s', username)

    user = User.query.filter_by(username=username).first()

    current_app.logger.info('User attempting log in: %s', user)

    if user:
        if user.is_active:
            if user.validate_password(password):
                login_user(user)
                current_app.logger.info('User logged in: %s', user.username)
                return user
    
    time.sleep(2)
    

def must_be_admin():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_admin:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator

