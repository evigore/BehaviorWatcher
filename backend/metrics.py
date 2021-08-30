"""
HTTP handlers for /metrics route
"""

from flask import make_response, abort, jsonify
from thirdparty import db, exc, and_
from models import (
		Metric, Verification, Error,
		MetricSchema, VerificationSchema, ErrorSchema)

errorSchema = ErrorSchema()
metricSchema = MetricSchema()
metricsSchema = MetricSchema(many=True)


def get(user_id=None, task_id=None):
    """
    Respond to a GET request for /api/metrics

    :return json array of metrics
    """
    try:
        if user_id is None and task_id is None:
            metrics = Metric.query.all()
            return metricsSchema.dump(metrics), 200

        if user_id is None:
            metrics = Metric.query.filter(Metric.task_id == task_id).all()
            return metricsSchema.dump(metrics), 200

        if task_id is None:
            metrics = Metric.query.filter(Metric.user_id == user_id).all()
            return metricsSchema.dump(metrics), 200

        metrics = Metric.query.filter(Metric.user_id.like(user_id) & Metric.task_id.like(task_id)).all()
        return metricsSchema.dump(metrics), 200
    except Exception:
        return errorSchema.dump(Error('Unexpected error')), 500


def post(Body):
    """
    Respond to a POST request for /api/metrics
    Creates new metric with metric data, assigns metric.id
    """

    try:
        result = Metric.query.filter(Metric.user_id.like(Body.get('user_id')) & Metric.task_id.like(Body.get('task_id'))).one_or_none()
        if result is not None:
            return patch(result.id, Body)
            #return errorSchema.dump(Error(f"Metric with user_id={Body['user_id']} and task_id={Body['task_id']} already exists.")), 400

        metric = Metric(**Body)
        db.session.add(metric)
        db.session.commit()

        return get_one(metric.id)[0]
    except TypeError as e:
        return errorSchema.dump(Error(str(e))), 400
    except Exception:
        return errorSchema.dump(Error("Unexpected error")), 500


def get_one(metricId):
    """
    Respond to a GET request for /api/metrics/{metricId}
    Returns specified metric

    :param metricId Id of the metric to read
    :return metric on success or 404
    """

    try:
        metric = Metric.query.filter(Metric.id.like(metricId)).one_or_none()
        if metric is None:
            return errorSchema.dump(Error(f"Metric with metricId={metricId} does not exists")), 400

        return metricSchema.dump(metric), 200
    except Exception:
        return errorSchema.dump(Error("Unexpected error")), 500


def patch(metricId, Body):
    """
    Respond to a PATCH request for /api/metrics/{metricId}
    Patches the metric with the properties of Body or leaves unchanged

    :param metricId             Id of the metric to update
    :param Body		            Data to update the metric with
    """

    try:
        metric = Metric.query.filter(Metric.id.like(metricId)).one_or_none()
        if metric is None:
            return errorSchema.dump(Error(f"Metric with metricId: {metricId} does not exists")), 400

        metric.user_id = Body.get('user_id')
        metric.task_id = Body.get('task_id')

        if Body.get('reading_time') is not None:
            metric.reading_time += max(0, int(Body.get('reading_time')))

        if Body.get('task_viewed') is not None:
            metric.task_viewed = metric.task_viewed or bool(Body.get('task_viewed'))

        if Body.get('task_copied') is not None:
            metric.task_copied = metric.task_copied or bool(Body.get('task_copied'))

        db.session.add(metric)
        db.session.commit()

        return metricSchema.dump(metric), 200
    except exc.IntegrityError:
        return errorSchema.dump(Error(f"Metric with user_id={metric.user_id} and task_id={metric.task_id} already exists")), 400
    except Exception:
        return errorSchema.dump(Error("Unexpected error")), 500


def delete(metricId):
    """
    Respond to a DELETE request for /api/metrics/{metricId}
    Deletes the metric

    :param metricId    Id of the metric to update
    """


    try:
        metric = Metric.query.filter(Metric.id.like(metricId)).one_or_none()
        if metric is None:
            return errorSchema.dump(Error(f"Metric with id {metricId} not found")), 400

        db.session.delete(metric)
        db.session.commit()

        return errorSchema.dump(Error("OK")), 200
    except Exception:
        return errorSchema.dump(Error("Unexpected error")), 500


