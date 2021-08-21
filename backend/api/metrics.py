"""
This is the 'metrics' module and supports all the REST actions for the
metric data
"""

from flask import make_response, abort
# from config import db
# from models import


def read_all(userId=None, taskId=None):
    """
    Respond to a GET request for /api/metrics

    :return json array of metrics
    """
    if userId is None:
        userId = 0
    if taskId is None:
        taskId = 0

    return [
        {
            "id": 0,
            "userId": taskId,
            "taskId": userId,
            "taskCopied": True,
            "taskViewed": True,
            "readingTime": 0
        }
    ]


def create(metric):
    """
    Respond to a POST request for /api/metrics
    Creates new metric with metric data, assigns metric.id

    :param metric   metric to create
    :return 201 on success, 409 if metric already exists
    """

    metric['id'] = 0
    # return metric, 201

    abort(
        409, f"Metric with userId: {metric['userId']} and taskId: {metric['taskId']} already exists."
    )


