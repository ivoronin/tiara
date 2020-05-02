from flask import Blueprint
from flask_restful import Api
import ipamd.resources as resources

bp = Blueprint("ipam", __name__)  # pylint: disable=C0103
api = Api(bp)

api.add_resource(resources.NetworkList, '/network')
api.add_resource(resources.Network, '/network/<int:network_id>')

api.add_resource(resources.RangeList, '/network/<int:network_id>/range')
api.add_resource(resources.Range, '/network/<int:network_id>/range/<int:range_id>')

api.add_resource(resources.AddressList, '/network/<int:network_id>/range/<int:range_id>/address')
api.add_resource(resources.Address, '/network/<int:network_id>/range/<int:range_id>/address/<int:address_id>')
