from flask_restful import marshal_with, reqparse
from netaddr import IPNetwork
from werkzeug.exceptions import BadRequest
from ipamd.db import db
import ipamd.models as models
from ipamd.resources.range import validate_range
from ipamd.resources.base import IPAMResource


class NetworkArgumentParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        self.add_argument('address', type=lambda n: IPNetwork(n), location='json', required=True)  # pylint: disable=W0108


def validate_network(network):
    networks = models.Network.query.with_for_update().all()
    for other in networks:
        # Object is being updated
        if network.id == other.id:
            for range_ in network.ranges:
                validate_range(network, range_)
        elif network.address in other.address or other.address in network.address:
            raise BadRequest(f"network {network.address} overlaps with other network {other.address}")


class NetworkList(IPAMResource):
    @marshal_with(models.Network.marshal_fields)
    def get(self):  # pylint: disable=R0201
        networks = models.Network.query.all()
        return networks

    @marshal_with(models.Network.marshal_fields)
    def post(self):  # pylint: disable=R0201
        args = NetworkArgumentParser().parse_args()
        network = models.Network(address=args['address'])
        validate_network(network)
        db.session.add(network)  # pylint: disable=E1101
        db.session.commit()  # pylint: disable=E1101
        return network


class Network(IPAMResource):
    @marshal_with(models.Network.marshal_fields)
    def get(self, network_id):  # pylint: disable=R0201
        network = models.Network.query.filter_by(id=network_id).first_or_404()
        return network

    @marshal_with(models.Network.marshal_fields)
    def put(self, network_id):  # pylint: disable=R0201
        network = models.Network.query.filter_by(id=network_id).first_or_404()
        args = NetworkArgumentParser().parse_args()
        network.address = args['address']
        validate_network(network)
        db.session.commit()  # pylint: disable=E1101
        return network

    def delete(self, network_id: int):  # pylint: disable=R0201
        network = models.Network.query.filter_by(id=network_id).first_or_404()
        db.session.delete(network)  # pylint: disable=E1101
        db.session.commit()  # pylint: disable=E1101
