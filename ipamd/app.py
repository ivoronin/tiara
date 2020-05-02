import os
from flask import Flask
from flask_migrate import Migrate
from ipamd.db import db
from ipamd import ipam
from ipamd import health

def create_app():  # pylint: disable=C0116
    app = Flask(__name__)

    username = os.getenv('IPAM_USERNAME', 'ipam')
    password = os.getenv('IPAM_PASSWORD', 'ipam')
    db_uri = os.getenv('IPAM_DATABASE_URI', 'sqlite:////data/ipam.db')

    app.config.from_mapping(
        USERNAME=username,
        PASSWORD=password,
        SQLALCHEMY_DATABASE_URI=db_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)
    migrate = Migrate()
    migrate.init_app(app, db)

    app.register_blueprint(ipam.bp)
    app.register_blueprint(health.bp)
    return app
