"""
HTTP handlers for /metrics route
"""

from flask import make_response, abort
from thirdparty import db
from models import (Metric, Verification, MetricSchema, VerificationSchema)

metric_schema = MetricSchema()
metrics_schema = MetricSchema(many=True)


def read_all(user_id=None, task_id=None):
    """
    Respond to a GET request for /api/metrics

    :return json array of metrics
        returns array with 1 element when user_id, task_id are specified
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


def create(Body):
    """
    Respond to a POST request for /api/metrics
    Creates new metric with metric data, assigns metric.id

    :return 201 on success, 409 if metric already exists
    """

    result = (Metric.query
              .filter(Metric.user_id == Body.get('user_id'))
              .filter(Metric.task_id == Body.get('task_id'))
              .one_or_none()
              )

    if result is None:
        new_metric = Metric(**Body)
        db.session.add(new_metric)
        db.session.commit()

        return metric_schema.dump(new_metric), 201

    abort(
        409, f"Metric with user_id: {Body['user_id']} and task_id: {Body['task_id']} already exists."
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


def patch(metricId, Body):
    """
    Respond to a PATCH request for /api/metrics/{metricId}
    Patches the metric with the properties of Body or leaves unchanged

    :param metricId             Id of the metric to update
    :param Body		            Data to update the metric with
    :return 200 on success
    """

    metric = (Metric.query
              .filter(Metric.id == metricId)
              .one_or_none()
              )

    if metric is None:
        abort(404, f"Metric with metricId: {metricId} does not exists.")

    #TODO if options are unset don't change metric
    metric.user_id = Body.get('user_id')
    metric.task_id = Body.get('task_id')
    metric.reading_time = Body.get('reading_time')
    metric.task_viewed = Body.get('task_viewed')
    metric.task_copied = Body.get('task_copied')

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
