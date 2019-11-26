#!/usr/bin/env python3

from flask_mail import Mail, Message
from flask import current_app

mail = Mail()


def init_mail(app):
    mail.init_app(app)


def email(subject, message, recipients, html=''):
    msg = Message(subject=subject, recipients=recipients, body=message, html=html)

    mail.send(msg)
