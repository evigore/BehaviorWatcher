"""
HTTP handlers for /receivers route
"""

from flask import make_response, abort
from db import db
from api.models import (
        Receiver, ReceiverSchema
)

receiver_schema = ReceiverSchema()
receivers_schema = ReceiverSchema(many=True)

def read_one(receiverId):
    """
    Respond to a GET request for /receivers/{receiverId}

    :return User object
    """
    receiver = Receiver.query.filter(Receiver.id == receiverId).one_or_none()

    if receiver is None:
        abort(404, f"Receiver with id: {receiverId} doesn't exist.")

    return receiver_schema.dump(receiver), 200


def delete(receiverId):
    """
    Respond to a DELETE request for /receivers/{receiverId}

    :param                  receiverId - id of receiver 
    :return                 200 on success, 404 on failure
    """
    receiver = Receiver.query.filter(Receiver.id == receiverId).one_or_none()
    if receiver is None:
        abort(404, f"Receiver with id: {receiverId} doesn't exist.")

    db.session.delete(receiver)
    db.session.commit()
    return make_response(f"Receiver with id {receiverId} deleted.", 200)
