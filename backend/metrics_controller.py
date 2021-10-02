"""
HTTP handlers for /metrics route
"""

from thirdparty import db
from models import (
    Error,
    ErrorSchema,
    Metric,
    MetricSchema,
)

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
    except Exception as e:
        print(e)
        return errorSchema.dump(Error('Unexpected error')), 500


def post(body):
    """
    Respond to a POST request for /api/metrics
    Creates new metric with metric data, assigns metric.id
    """

    try:
        result = Metric.query.filter(
            Metric.user_id.like(body.get('user_id')) & Metric.task_id.like(body.get('task_id'))).one_or_none()
        if result is not None:
            return patch(result.id, body)
            # return errorSchema.dump(Error(f"Metric with user_id={Body['user_id']} and task_id={Body['task_id']} already exists.")), 400

        metric = Metric(**body)
        db.session.add(metric)
        db.session.commit()

        return get_one(metric.id)[0]
    except TypeError as e:
        return errorSchema.dump(Error(str(e))), 400
    except Exception as e:
        print(e)
        return errorSchema.dump(Error("Unexpected error")), 500


def get_one(metric_id):
    """
    Respond to a GET request for /api/metrics/{metricId}
    Returns specified metric

    :param metric_id Id of the metric to read
    :return metric on success or 404
    """

    try:
        metric = Metric.query.filter(Metric.id.like(metric_id)).one_or_none()
        if metric is None:
            return errorSchema.dump(Error(f"Metric with metricId={metric_id} does not exists")), 400

        return metricSchema.dump(metric), 200
    except Exception as e:
        print(e)
        return errorSchema.dump(Error("Unexpected error")), 500


def patch(metric_id, body):
    """
    Respond to a PATCH request for /api/metrics/{metricId}
    Patches the metric with the properties of Body or leaves unchanged

    :param metric_id             Id of the metric to update
    :param body		            Data to update the metric with
    """

    try:
        metric = Metric.query.filter(Metric.id.like(metric_id)).one_or_none()
        if metric is None:
            return errorSchema.dump(Error(f"Metric with metricId: {metric_id} does not exists")), 400

        metric.user_id = body.get('user_id')
        metric.task_id = body.get('task_id')

        if body.get('reading_time') is not None:
            metric.reading_time += max(0, int(body.get('reading_time')))

        if body.get('task_viewed') is not None:
            metric.task_viewed = metric.task_viewed or bool(body.get('task_viewed'))

        if body.get('task_copied') is not None:
            metric.task_copied = metric.task_copied or bool(body.get('task_copied'))

        db.session.add(metric)
        db.session.commit()

        return metricSchema.dump(metric), 200
    except db.exc.IntegrityError:
        return errorSchema.dump(
           Error(f"Metric with user_id={metric.user_id} and task_id={metric.task_id} already exists")), 400
    except Exception as e:
        print(e)
        return errorSchema.dump(Error("Unexpected error")), 500


def delete(metric_id):
    """
    Respond to a DELETE request for /api/metrics/{metricId}
    Deletes the metric

    :param metric_id    Id of the metric to update
    """

    try:
        metric = Metric.query.filter(Metric.id.like(metric_id)).one_or_none()
        if metric is None:
            return errorSchema.dump(Error(f"Metric with id {metric_id} not found")), 400

        db.session.delete(metric)
        db.session.commit()

        return errorSchema.dump(Error("OK")), 200
    except Exception as e:
        print(e)
        return errorSchema.dump(Error("Unexpected error")), 500
