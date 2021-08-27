"""
HTTP handlers for /metrics route
"""

from flask import make_response, abort
from db import db
from api.models import (
    Metric, Sender, Receiver,
    MetricSchema, SenderSchema, ReceiverSchema
)

metric_schema = MetricSchema()
metrics_schema = MetricSchema(many=True)

sender_schema = SenderSchema()
senders_schema = SenderSchema(many=True)

receiver_schema = ReceiverSchema()
receivers_schema = ReceiverSchema(many=True)


def read_all(user_id=None, task_id=None):
    """
    Respond to a GET request for /api/metrics

    :return json array of metrics
    """
    if user_id is None and task_id is None:
        metrics = Metric.query.all()
        return metrics_schema.dump(metrics), 200

    if user_id is None:
        metrics = Metric.query.filter(Metric.task_id == task_id).all()
        return metrics_schema.dump(metrics), 200

    if task_id is None:
        metrics = Metric.query.filter(Metric.user_id == user_id).all()
        return metrics_schema.dump(metrics), 200


def create(metric):
    """
    Respond to a POST request for /api/metrics
    Creates new metric with metric data, assigns metric.id

    :param metric   metric to create
    :return 201 on success, 409 if metric already exists
    """

    result = (Metric.query
              .filter(Metric.user_id == metric.get('user_id'))
              .filter(Metric.task_id == metric.get('task_id'))
              .one_or_none()
              )

    if result is None:
        new_metric = Metric(**metric)
        db.session.add(new_metric)
        db.session.commit()

        return metric_schema.dump(new_metric), 201
    abort(
        409, f"Metric with user_id: {metric['user_id']} and task_id: {metric['task_id']} already exists."
    )


def read_one(metricId):
    """
    Respond to a GET request for /api/metrics/{metricId}
    Returns specified metric

    :param metricId Id of the metric to read
    :return metric on success or 404
    """
    metric = (Metric.query
              .filter(Metric.id == metricId)
              .one_or_none()
              )

    if metric is None:
        abort(404, f"Metric with metricId: {metricId} does not exists.")
    else:
        return metric_schema.dump(metric), 200


def patch(metricId, metricData):
    """
    Respond to a PATCH request for /api/metrics/{metricId}
    Patches the metric with the properties of metricData or leaves unchanged

    :param metricId             Id of the metric to update
    :param metricData           Data to update the metric with
    :return 200 on success
    """
    metric = (Metric.query
        .filter(Metric.id == metricId)
        .one_or_none()
      )

    if metric is None:
        abort(404, f"Metric with metricId: {metricId} does not exists.")
    else:
        metric.user_id = metricData.get('user_id')
        metric.task_id = metricData.get('task_id')
        metric.reading_time = metricData.get('reading_time')
        metric.task_viewed = metricData.get('task_viewed')
        metric.task_copied = metricData.get('task_copied')

        db.session.add(metric)
        db.session.commit()
        
        return metric_schema.dump(metric), 200


def delete(metricId):
    """
    Respond to a DELETE request for /api/metrics/{metricId}
    Deletes the metric

    :param metricId    Id of the metric to update
    :return 200 on success, 404 on failure
    """
    metric = Metric.query.filter(Metric.id == metricId).one_or_none()
    if metric is None:
        abort(404, f"Metric with id {metricId} not found.")
    else:
        db.session.delete(metric)
        db.session.commit()
        return make_response(f"Metric with id {metricId} deleted.", 200)



def read_receivers(metricId):
    """
    Respond to a GET request for /api/metrics/{metricId}/receivers
    Return array of receivers

    :param metricId    Id of the metric to update
    :return 200|204 on success
    """
    metric = Metric.query.filter(Metric.id == metricId).one_or_none()
    if metric is None:
        abort(404, f"Metric with id {metricId} not found.")
    receivers = Receiver.query.with_parent(metric).all()
    return receivers_schema.dump(receivers), 200



def create_receiver(metricId, receiverData):
    """
    Respond to a POST request for /api/metrics/{metricId}/receivers
    Add new receiver to concrete metric

    :param metricId             Id of the metric to update
    :param receiverData         Object with 1 property (user_id)
    :return 201 on success, 409 if metric already exists
    """
    metric = Metric.query.filter(Metric.id == metricId).one_or_none()

    if metric is None:
        abort(
            409, f"Metric with metricId: {metricId} doesn't exists."
        )
    
    user_id = receiverData.get('user_id')
    receiver = (Receiver.query
        .with_parent(metric)
        .filter(Receiver.user_id == user_id)
        .filter(Receiver.metric_id == metricId)
        .one_or_none()
    )

    if receiver is not None:
        abort(
            409, f"Metric {metricId} already has receiver with user_id: {user_id}, metric_id: {metricId}"
        )

    receiver = Receiver(user_id=user_id, metric_id=metricId)
    metric.receivers.append(receiver)
    db.session.add(receiver)
    db.session.commit()
    return receiverData, 201


def read_senders(metricId):
    """
    Respond to a GET request for /api/metrics/{metricId}/senders
    Return array of senders

    :param metricId                         Id of the metric to update
    :return 200|204 on success
    """
    metric = Metric.query.filter(Metric.id == metricId).one_or_none()
    if metric is not None:
        abort(404, f"Metric with id {metricId} not found.")
    senders = Sender.query.with_parent(metric).all()
    return senders_schema.dump(senders)




def create_sender(metricId, senderData):
    """
    Respond to a POST request for /api/metrics/{metricId}/sender
    Add new receiver to concrete metric

    :param metricId         Id of the metric to update
    :param senderData       Object with 1 property (user_id) 
    :return 201 on success, 409 if metric already exists
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

