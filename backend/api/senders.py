"""
HTTP handlers for /senders route
"""

from flask import make_response, abort
from db import db
from api.models import (
        Sender, SenderSchema
)

sender_schema = SenderSchema()
senders_schema = SenderSchema(many=True)

def read_one(senderId):
    """
    Respond to a GET request for /senders/{senderId}

    :return User object
    """
    sender = Sender.query.filter(Sender.id == senderId).one_or_none()

    if sender is None:
        abort(404, f"Sender with id: {senderId} doesn't exist.")

    return sender_schema.dump(sender), 200


def delete(senderId):
    """
    Respond to a DELETE request for /senders/{senderId}

    :param                  senderId - id of sender 
    :return                 200 on success, 404 on failure
    """
    sender = Sender.query.filter(Sender.id == senderId).one_or_none()
    if sender is None:
        abort(404, f"Sender with id: {senderId} doesn't exist.")

    db.session.delete(sender)
    db.session.commit()
    return make_response(f"Sender with id {senderId} deleted.", 200)
