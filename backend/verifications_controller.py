"""
HTTP handlers for /verification route
"""

from Thirdparty import db, fetch
import filter
import json
from flask import jsonify
import metrics
from models import (Metric, Verification, Error, VerificationSchema, ErrorSchema)

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


def get_one(solutionId):
	try:
		# get user id and task id
		verification = Verification.query.filter(Verification.destination_solution_id.like(solutionId) & Verification.verdict_of_human.is_(True)).first()
		user_id = None
		task_id = None
		if verification is not None:
			user_id = verification.destination_user_id
			task_id = verification.task_id

		# get user rating
		rating = metrics.get_user_rating(user_id) if verification else None

		# get task_copied, task_viewed and reading_time
		metric = Metric.query.filter(Metric.user_id.like(user_id) & Metric.task_id.like(task_id)).one_or_none()
		reading_time = metric.reading_time
		task_copied = False
		task_viewed = False
		if metric:
			task_copied = metric.task_viewed
			task_viewed = metric.task_copied

		# time reading + number of attempts
		solutions = fetch(db.engine.execute("SELECT OwnerId, COUNT(OwnerId) AS attempts FROM Solution WHERE TestTaskId='ff1636d5-0aab-479c-9aa2-b14271d8cdf2' GROUP BY OwnerId ORDER BY attempts", {
			#'task_id': target_solution['TestTaskId'] # TODO: change to real task id
		}))
		user_id = 'e7c8a6c6-b73c-4179-8cb0-45bfcfea9ca5' # TODO: delete
		average_attempts = 0
		user_attempts = 0
		for solution in solutions:
			average_attempts += solution['attempts']
			if solution['OwnerId'] == user_id:
				user_attempts = solution['attempts']
		average_attempts /= len(solutions)

		time_and_attempts = ''
		if reading_time < 3:
			time_and_attempts = 'Пользователь не читал задание'
		elif user_attempts < average_attempts:
			time_and_attempts = 'Пользователь решил задание за меньше среднего количества попыток'
		elif user_attempts >= average_attempts:
			time_and_attempts = 'Пользователь решил задание за больше среднего количества попыток'

	
		# order of solution
		#solutions = fetch(db.engine.execute("SELECT OwnerId, CreatedAt FROM Solution WHERE TestTaskId='ff1636d5-0aab-479c-9aa2-b14271d8cdf2' AND FailedTest IS NULL GROUP BY OwnerId", {
			##'task_id': target_solution['TestTaskId'] # TODO: change to real task id
		#}))
		#solutions.sort(reverse=True, key=lambda i: i['CreatedAt'])
		#print(solutions[0], solutions[1])


		report = {
			'rating': rating,
			'task_viewed': task_viewed,
			'task_copied': task_copied,
			'time_and_attempts': time_and_attempts
		}

		return jsonify(report), 200
	except Exception as e:
		print(str(e))
		return errorSchema.dump(Error("Unexpected error")), 500



def post(solutionId):
	try:
		# 1. Get solution entity with userId, task, etc from other DB
		solutionId = 1

		# 2. filter users (filter.py)
		filter(solutionId)

		# 3. call API of other module

		# apiResponse = request(...) # TODO: real request
		response = json.loads(apiResponse)
		for i in response['Scores']:
			verification = Verification(**{
				'source_solution_id': i['SolutionID'],
				'destination_solution_id': solutionId,
				'source_user_id': 4, # TODO: change to real id
				'destination_user_id': 6, # TODO: change to real id
				'task_id': 59, # TODO: change to real id
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
		print(str(e)) # TODO: delete
		return errorSchema.dump(Error("Unexpected error")), 500


def patch(solutionId, Body):
	try: 
		if Body.get('is_plagiarism'):
			Verification.query.filter(Verification.destination_solution_id == solutionId).update({Verification.verdict_of_human: True})
		else:
			Verification.query.filter(Verification.destination_solution_id == solutionId).delete();

		db.session.commit()
		return errorSchema.dump(Error("OK")), 200
	except Exception:
		return errorSchema.dump(Error("Unexpected error")), 500



