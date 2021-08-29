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
