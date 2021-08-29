"""
HTTP handlers for /verification route
"""

from flask import make_response, abort
from thirdparty import db
from api.models import (Verification, VerificationSchema)

def get_verification_of_solution(solutionId):
	pass

def post_verification_of_solution(solutionId):
	pass

def patch_verdict_of_solution(solutionId):
	pass

"""
verification_schema = VerificationSchema()
verifications_schema = VerificationSchema(many=True)

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
"""


#def read_senders(metricId):
    """
    Respond to a GET request for /api/metrics/{metricId}/senders
    Return array of senders

    :param metricId                         Id of the metric to update
    :return 200|204 on success
    """
	"""
    metric = Metric.query.filter(Metric.id == metricId).one_or_none()
    if metric is not None:
        abort(404, f"Metric with id {metricId} not found.")
    senders = Sender.query.with_parent(metric).all()
    return senders_schema.dump(senders)
	"""



#def create_sender(metricId, senderData):
    """
    Respond to a POST request for /api/metrics/{metricId}/sender
    Add new receiver to concrete metric

    :param metricId         Id of the metric to update
    :param senderData       Object with 1 property (user_id) 
    :return 201 on success, 409 if metric already exists
    """
	"""
    metric = Metric.query.filter(Metric.id == metricId).one_or_none()

    if metric is None:
        abort(
            409, f"Metric with metricId: {metricId} doesn't exists."
        )
    
    user_id = senderData.get('user_id')
    sender = (Sender.query
        .with_parent(metric)
        .filter(Sender.user_id == user_id)
        .filter(Sender.metric_id == metricId)
        .one_or_none()
    )

    if sender is not None:
        abort(
            409, f"Metric {metricId} already has sender with user_id: {user_id}, metric_id: {metricId}"
        )

    sender = Sender(user_id=user_id, metric_id=metricId)
    metric.senders.append(sender)
    db.session.add(sender)
    db.session.commit()
    return senderData, 201
	"""
