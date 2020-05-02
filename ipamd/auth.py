from flask_httpauth import HTTPBasicAuth
from flask import current_app as app

auth = HTTPBasicAuth()  # pylint: disable=C0103


@auth.verify_password
def verify_password(username, password):
    """Called by flask_httpauth"""
    if username == app.config['USERNAME']:
        return password == app.config['PASSWORD']
    return False
