from flask_restful import marshal_with, reqparse
from netaddr import IPAddress
from werkzeug.exceptions import BadRequest
from ipamd.db import db
import ipamd.models as models
from ipamd.resources.base import IPAMResource


class RangeArgumentParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        self.add_argument('start', type=lambda a: IPAddress(a), location='json', required=True)  # pylint: disable=W0108
        self.add_argument('stop', type=lambda a: IPAddress(a), location='json', required=True)  # pylint: disable=W0108


def validate_range(network: models.Network, range_: models.Range):
    # Sanity checks
    if range_.start > range_.stop:
        raise BadRequest(f"{range_.start} is greater than {range_.stop}")
    if range_.range.first not in network.address or range_.range.last not in network.address:
        raise BadRequest(f"range {range_.range} is out of {network.address} bounds")
    if network.address.network in range_.range:
        raise BadRequest(f"{network.address.network} is a network address")
    if network.address.broadcast in range_.range:
        raise BadRequest(f"{network.address.network} is a broadcast address")

    ranges = models.Range.query.filter_by(network=network).with_for_update().all()
    for other in ranges:
        # Object is being updated
        if range_.id == other.id:
            for address in range_.addresses:
                if address.address not in range_.range:
                    raise BadRequest(f"address {address.address} is out of range {range_.range}")
        elif range_.range.first in other.range or range_.range.last in other.range:
            raise BadRequest(f"range {range_.range} overlaps with other range {other.range}")


class RangeList(IPAMResource):
    @marshal_with(models.Range.marshal_fields)
    def get(self, network_id: int):  # pylint: disable=R0201
        return models.Range.query.filter_by(network_id=network_id).all()

    @marshal_with(models.Range.marshal_fields)
    def post(self, network_id: int):  # pylint: disable=R0201
        network = models.Network.query.get_or_404(network_id)
        args = RangeArgumentParser().parse_args()
        range_ = models.Range(network=network, start=args['start'], stop=args['stop'])
        validate_range(network, range_)
        db.session.add(range_)  # pylint: disable=E1101
        db.session.commit()  # pylint: disable=E1101
        return range_


class Range(IPAMResource):
    @marshal_with(models.Range.marshal_fields)
    def get(self, network_id: int, range_id: int):  # pylint: disable=R0201
        range_ = models.Range.query.filter_by(id=range_id, network_id=network_id).first_or_404()
        return range_

    @marshal_with(models.Range.marshal_fields)
    def put(self, network_id: int, range_id: int):  # pylint: disable=R0201
        network = models.Network.query.get_or_404(network_id)
        range_ = models.Range.query.filter_by(id=range_id, network=network).first_or_404()
        args = RangeArgumentParser().parse_args()
        range_.start = args['start']
        range_.stop = args['stop']
        validate_range(network, range_)
        db.session.commit()  # pylint: disable=E1101
        return range_

    def delete(self, network_id: int, range_id: int):  # pylint: disable=R0201
        range_ = models.Range.query.filter_by(id=range_id, network_id=network_id).first_or_404()
        db.session.delete(range_)  # pylint: disable=E1101
        db.session.commit()  # pylint: disable=E1101
