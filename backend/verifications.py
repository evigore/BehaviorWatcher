"""
HTTP handlers for /verification route
"""

from flask import make_response, abort
from thirdparty import db
from models import (Verification, Error, VerificationSchema, ErrorSchema)

errorSchema = ErrorSchema()
verificationSchema = VerificationSchema()

def get_one(solutionId):
    """
    Respond to a GET request for /verifications/{solutionId}
    Returns specified verification

    :param solutionId           Id of the verification to return
    :return (verification, 200) | (404)
    """
	
    #verification = Verification.query.filter(Verification.id == solutionId).one_or_none()
    #if verification is None:
        #errorSchema.dump(Error(f"Metric with metricId: {solutionId} does not exists")), 400

    #return verificationSchema.dump(verification), 200
	
	# 1. Get solution entity with userId, task, etc from other DB
	# 2. Get another data
	# 4. Calculate something
	# 5. ...
	# 6. Magic
	# 7. Profit

	# 1. K
	# 2. I
	# 4. L
	# 5. L
	# 6. M
	# 7. E


def post(solutionId):
    """
    Does some strange shit that I don't know about
    """

	# 1. Get solution entity with userId, task, etc from other DB
	# 2. filter users (filter.py)
	# 3. call API of other module
	# 4. save result to our DB (especially to Verification TABLE)
	# 5. Is it all?
    pass


def patch(solutionId, Body):
    """
    Partionally update the verification with data in Body

    :return (verification, 200) | 404
    """
	# 1. If is_plagiarism == TRUE, then: for all verifications WHERE destination_solution_id == solutionId SET verdict_of_human=TRUE
	# 2. Else: DELETE Verifications WHERE destination_solution_id == solutionId
    pass


"""
verificationSchema = VerificationSchema()
verificationsSchema = VerificationSchema(many=True)

def read_one(senderId):
"""
"""
    Respond to a GET request for /senders/{senderId}

    :return User object
    """"""
    sender = Sender.query.filter(Sender.id == senderId).one_or_none()

    if sender is None:
        abort(404, f"Sender with id: {senderId} doesn't exist.")

    return senderSchema.dump(sender), 200


def delete(senderId):
	""""""
    Respond to a DELETE request for /senders/{senderId}

    :param                  senderId - id of sender 
    :return                 200 on success, 404 on failure
    """"""
    sender = Sender.query.filter(Sender.id == senderId).one_or_none()
    if sender is None:
        abort(404, f"Sender with id: {senderId} doesn't exist.")

    db.session.delete(sender)
    db.session.commit()
    return make_response(f"Sender with id {senderId} deleted.", 200)
	"""

# def read_senders(metricId):
"""
    Respond to a GET request for /api/metrics/{metricId}/senders
    Return array of senders

    :param metricId                         Id of the metric to update
    :return 200|204 on success
    """"""
    metric = Metric.query.filter(Metric.id == metricId).one_or_none()
    if metric is not None:
        abort(404, f"Metric with id {metricId} not found.")
    senders = Sender.query.with_parent(metric).all()
    return sendersSchema.dump(senders)
	"""


# def create_sender(metricId, senderData):
"""
    Respond to a POST request for /api/metrics/{metricId}/sender
    Add new receiver to concrete metric

    :param metricId         Id of the metric to update
    :param senderData       Object with 1 property (user_id) 
    :return 201 on success, 409 if metric already exists
    """"""
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
