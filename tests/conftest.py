from base64 import b64encode
import os
import tempfile
import pytest
from flask.testing import FlaskClient
from flask_migrate import upgrade
from werkzeug.datastructures import Headers
from ipamd import create_app


class AuthenticatedClient(FlaskClient):  # pylint: disable=C0115
    def __init__(self, *args, **kwargs):
        username = kwargs.pop('username')
        password = kwargs.pop('password')
        self._credentials = b64encode(f'{username}:{password}'.encode('utf-8')).decode('utf-8')
        super().__init__(*args, **kwargs)

    def open(self, *args, **kwargs):
        headers = kwargs.pop('headers', Headers())
        # https://github.com/pallets/werkzeug/blob/master/src/werkzeug/test.py
        if headers is None:
            headers = Headers()
        elif not isinstance(headers, Headers):
            headers = Headers(headers)
        credentials = kwargs.pop('credentials', self._credentials)
        disable_auth = kwargs.pop('disable_auth', False)
        if not disable_auth:
            headers.extend(Headers({"Authorization": f"Basic {credentials}"}))
            kwargs['headers'] = headers
        return super().open(*args, **kwargs)


@pytest.fixture
def client():  # pylint: disable=C0116
    with tempfile.NamedTemporaryFile() as db_file:
        os.environ['IPAM_DATABASE_URI'] = f'sqlite:///{db_file.name}'
        app = create_app()
        app.test_client_class = AuthenticatedClient
        with app.app_context():
            upgrade()
            username = app.config['USERNAME']
            password = app.config['PASSWORD']
        with app.test_client(username=username, password=password) as test_client:
            yield test_client
