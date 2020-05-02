from flask_restful import Resource
from ipamd.auth import auth


class IPAMResource(Resource):
    method_decorators = [auth.login_required]
