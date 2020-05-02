from flask_restful import marshal_with, reqparse, abort
from ipamd.db import db
import ipamd.models as models
from ipamd.resources.base import IPAMResource


class AddressRequestParser(reqparse.RequestParser):
    def __init__(self):
        super().__init__()
        self.add_argument('name', type=str, location='json', required=True)


class AddressList(IPAMResource):
    @marshal_with(models.Address.marshal_fields)
    def get(self, network_id, range_id):  # pylint: disable=R0201, W0613
        addresses = models.Address.query.filter_by(range_id=range_id).all()
        return addresses

    @marshal_with(models.Address.marshal_fields)
    def post(self, network_id, range_id):  # pylint: disable=R0201
        range_ = models.Range.query.filter_by(id=range_id, network_id=network_id).with_for_update().first_or_404()
        args = AddressRequestParser().parse_args()
        for ip_address in range_.range:
            if not ip_address in [a.address for a in range_.addresses]:
                address = models.Address(address=ip_address, name=args['name'], range=range_)
                db.session.add(address)  # pylint: disable=E1101
                db.session.commit()  # pylint: disable=E1101
                break
        else:
            abort(404, error=f'no more addresses are available in range {range_.range}')
        return address


class Address(IPAMResource):
    @marshal_with(models.Address.marshal_fields)
    def get(self, network_id, range_id, address_id):  # pylint: disable=R0201,W0613
        address = models.Address.query.filter_by(id=address_id, range_id=range_id).first_or_404()
        return address

    def delete(self, network_id, range_id, address_id):  # pylint: disable=R0201,W0613
        address = models.Address.query.filter_by(id=address_id, range_id=range_id).first_or_404()
        db.session.delete(address)  # pylint: disable=E1101
        db.session.commit()  # pylint: disable=E1101

    def put(self, network_id, range_id, address_id):  # pylint: disable=R0201,W0613
        address = models.Address.query.filter_by(id=address_id, range_id=range_id).first_or_404()
        args = AddressRequestParser().parse_args()
        address.name = args['name']
        db.session.commit()  # pylint: disable=E1101
        return address
