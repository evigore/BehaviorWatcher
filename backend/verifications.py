"""
HTTP handlers for /verification route
"""
import json
import filter

from thirdparty import db
from models import (Verification, Error, VerificationSchema, ErrorSchema)

errorSchema = ErrorSchema()
verificationSchema = VerificationSchema()

apiResponse = """{
    "Version": "1",
    "SolutionID": "original.py",
    "MaxSimilarity": 0.9806427276796765,
    "MaxSimilaritySolutionID": "different_comments.py",
    "Verdict": "CLEAR POSITIVE",
    "Scores": [
        {
            "SolutionID": "different_comments.py",
            "TotalScore": 0.9806427276796765,
            "TextBasedScore": 1,
            "TokenBasedScore": 0.9955476522445679,
            "MetricBasedScore": 0.9444444444444444,
            "BinaryBasedScore": 0.9825788140296936,
            "TreeBasedScore": null
        },
        {
            "SolutionID": "reformatted.py",
            "TotalScore": 0.971757612294621,
            "TextBasedScore": 0.9889094233512878,
            "TokenBasedScore": 0.9714533090591431,
            "MetricBasedScore": 0.9444444444444444,
            "BinaryBasedScore": 0.9822232723236084,
            "TreeBasedScore": null
        },
        {
            "SolutionID": "renamed_variables.py",
            "TotalScore": 0.9180482551455498,
            "TextBasedScore": 0.7295423150062561,
            "TokenBasedScore": 1,
            "MetricBasedScore": 1,
            "BinaryBasedScore": 0.942650705575943,
            "TreeBasedScore": null
        },
        {
            "SolutionID": "reordered.py",
            "TotalScore": 0.9036459699273109,
            "TextBasedScore": 0.8485981523990631,
            "TokenBasedScore": 0.9040516316890717,
            "MetricBasedScore": 1,
            "BinaryBasedScore": 0.861934095621109,
            "TreeBasedScore": null
        },
        {
            "SolutionID": "with_additional_imports.py",
            "TotalScore": 0.8646872325075997,
            "TextBasedScore": 0.8857616186141968,
            "TokenBasedScore": 0.9573742747306824,
            "MetricBasedScore": 0.8888888888888888,
            "BinaryBasedScore": 0.7267241477966309,
            "TreeBasedScore": null
        },
        {
            "SolutionID": "with_functions.py",
            "TotalScore": 0.5494582574400637,
            "TextBasedScore": 0.4490084946155548,
            "TokenBasedScore": 0.679684579372406,
            "MetricBasedScore": 0.7222222222222222,
            "BinaryBasedScore": 0.3469177335500717,
            "TreeBasedScore": null
        }
    ]
}"""


def get_one(solution_id):
    """
    Respond to a GET request for /verifications/{solutionId}
    Returns specified verification

    :param solution_id           Id of the verification to return
    :return (verification, 200) | (404)
    """


# verification = Verification.query.filter(Verification.id == solutionId).one_or_none()
# if verification is None:
# errorSchema.dump(Error(f"Metric with metricId: {solutionId} does not exists")), 400

# return verificationSchema.dump(verification), 200

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


def post(solution_id):
    try:
        # 1. Get solution entity with userId, task, etc from other DB
        solution_id = 1

        # 2. filter users (filter.py)
        filter(solution_id)

        # 3. call API of other module

        # apiResponse = request(...) # TODO: real request
        response = json.loads(apiResponse)
        for i in response['Scores']:
            verification = Verification(**{
                'source_solution_id': i['SolutionID'],
                'destination_solution_id': solution_id,
                'source_user_id': 4,  # TODO: change to real id
                'destination_user_id': 6,  # TODO: change to real id
                'task_id': 59,  # TODO: change to real id
                'verdict_of_module': response['Verdict'],
                'total_score': i['TotalScore'],
                'text_based_score': i['TextBasedScore'],
                'token_based_score': i['TokenBasedScore'],
                'metric_based_score': i['MetricBasedScore'],
                'binary_based_score': i['BinaryBasedScore'],
                'tree_based_score': i['TreeBasedScore']
            })

            db.session.add(verification)

        # 4. save result to our DB (especially to Verification TABLE)
        db.session.commit()

        return errorSchema.dump(Error("OK")), 200
    except Exception as e:
        print(str(e))  # TODO: delete
        return errorSchema.dump(Error("Unexpected error")), 500


def patch(solution_id, body):
    try:
        if body.get('is_plagiarism'):
            Verification.query.filter(Verification.destination_solution_id == solution_id).update(
                {Verification.verdict_of_human: True})
        else:
            Verification.query.filter(Verification.destination_solution_id == solution_id).delete();

        db.session.commit()
        return errorSchema.dump(Error("OK")), 200
    except Exception as e:
        print(e)
        return errorSchema.dump(Error("Unexpected error")), 500
