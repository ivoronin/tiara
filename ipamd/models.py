# pylint: disable=E1101
from datetime import datetime
from flask_restful import fields
from netaddr import IPNetwork, IPAddress, IPRange
from ipamd.db import db


class IPAddressType(db.TypeDecorator):
    impl = db.String(64)

    def process_bind_param(self, value: IPAddress, dialect):  # pylint: disable=W0613,R0201
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value: str, dialect):  # pylint: disable=W0613,R0201
        if value is not None:
            return IPAddress(value)
        return value


class IPNetworkType(db.TypeDecorator):
    impl = db.String(64)

    def process_bind_param(self, value: IPNetwork, dialect):  # pylint: disable=W0613,R0201
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value: str, dialect):  # pylint: disable=W0613,R0201
        if value is not None:
            return IPNetwork(value)
        return value


class Network(db.Model):  # pylint: disable=R0903
    __tablename__ = 'networks'

    marshal_fields = {'id': fields.Integer, 'address': fields.String}

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    address = db.Column(IPNetworkType, nullable=False, unique=True)
    ranges = db.relationship('Range', backref=db.backref('network'), cascade="all, delete-orphan")

    @db.validates('address')
    def validate_address(self, key: str, value: IPNetwork):  # pylint: disable=W0613,R0201
        assert type(value) is IPNetwork  # pylint: disable=C0123
        return value


class Range(db.Model):  # pylint: disable=R0903
    __tablename__ = 'ranges'

    marshal_fields = {
        'id': fields.Integer,
        'network_id': fields.Integer,
        'start': fields.String,
        'stop': fields.String,
    }

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    network_id = db.Column(db.Integer, db.ForeignKey('networks.id'), index=True, nullable=False)
    addresses = db.relationship('Address', backref=db.backref('range'), cascade="all, delete-orphan")
    start = db.Column(IPAddressType, nullable=False)
    stop = db.Column(IPAddressType, nullable=False)

    @property
    def range(self):
        return IPRange(self.start, self.stop)

    @db.validates('start', 'stop')
    def validate_address(self, key: str, value: IPAddress):  # pylint: disable=W0613,R0201
        assert type(value) is IPAddress  # pylint: disable=C0123
        return value


class Address(db.Model):  # pylint: disable=R0903
    __tablename__ = 'addresses'

    marshal_fields = {
        'id': fields.Integer,
        'range_id': fields.Integer,
        'name': fields.String,
        'address': fields.String,
    }

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    range_id = db.Column(db.Integer, db.ForeignKey('ranges.id'), index=True, nullable=False)
    name = db.Column(db.String(128), nullable=True)
    address = db.Column(IPAddressType, nullable=False, unique=True)

    @db.validates('address')
    def validate_address(self, key: str, value: IPAddress):  # pylint: disable=W0613,R0201
        assert type(value) is IPAddress  # pylint: disable=C0123
        return value
