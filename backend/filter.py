from generator import *
from Thirdparty import db, fetch
from models import (Metric, Verification, Error, VerificationSchema, ErrorSchema)
import metrics
from datetime import datetime, timedelta
import sys

SUSPECT_AMOUNT = 30

LAST_SOLUTIONS_RATIO = 0.8
RATING_RATIO = 0.2

LAST_SOLUTIONS_AMOUNT = round(SUSPECT_AMOUNT * LAST_SOLUTIONS_RATIO)
RATING_AMOUNT = round(SUSPECT_AMOUNT * RATING_RATIO)


def remove_solutions_by_id(solutions, ids):
	l = []

	for solution in solutions:
		if solution['Id'] not in ids:
			l.append(solution)

	solutions.clear()
	solutions.extend(l)


def get_priority_solutions_ids(solutions):
	# TODO: Change 5 to target.user_id
	priority_verifications = Verification.query.filter(Verification.destination_user_id.like(5) & Verification.verdict_of_human.is_(True)).all()
	priority_users_ids = set([i.source_user_id for i in priority_verifications])

	priority_solutions_ids = []
	for solution in solutions:
		if solution['OwnerId'] in priority_users_ids:
			priority_solutions_ids.append(solution['Id'])

	return priority_solutions_ids


def get_last_solutions_since(date, solutions):
	solutions.sort(reverse=True, key=lambda i: i['CreatedAt'])

	start_index = -1
	for i, solution in enumerate(solutions):
		if solution['CreatedAt'] <= date:
			start_index = i
			break

	if start_index == -1:
		return []

	return solutions[start_index:]


def get_top_solutions_ids_by_rating(solutions):
	users_ratings = {}
	for id in set([i['OwnerId'] for i in solutions]):
		users_ratings[id] = metrics.get_user_rating(id)

	for i in solutions:
		i['Rating'] = users_ratings[i['OwnerId']]

	solutions.sort(reverse=True, key=lambda i: i['Rating'])

	top_solutions_ids = []
	for solution in solutions[0:RATING_AMOUNT]:
		#if solution['Rating'] == 0: # TODO: uncomment
			#break

		top_solutions_ids.append(solution['Id'])

	return top_solutions_ids


def main(target_solution_id):
	# TODO: Use real target solution id
	#target_solution = db.engine.execute("SELECT * FROM Solution WHERE Id=:id FailedTest IS NULL", {'id': target_solution_id}).first()
	target_solution = fetch(db.engine.execute("SELECT * FROM Solution WHERE TestTaskId='ff1636d5-0aab-479c-9aa2-b14271d8cdf2' AND FailedTest IS NULL LIMIT 1"))
	if len(target_solution) == 0:
		return
	target_solution = target_solution[0]


	solutions = fetch(db.engine.execute("SELECT Id, OwnerId, CreatedAt FROM Solution WHERE FailedTest IS NULL AND OwnerId<>:user_id AND TestTaskId=:task_id AND ProgramingLanguageId=:language_id", {
		'user_id': target_solution['OwnerId'],
		'task_id': target_solution['TestTaskId'],
		'language_id': target_solution['ProgramingLanguageId']
	})) # TODO: also check by class_id/university_id later. target.createdat < i.createdAt

	solutions = get_last_solutions_since(target_solution['CreatedAt'], solutions)


	priority_solutions_ids = get_priority_solutions_ids(solutions)
	remove_solutions_by_id(solutions, priority_solutions_ids)

	# TODO: Check to other classes
	top_solutions_ids = get_top_solutions_ids_by_rating(solutions)
	remove_solutions_by_id(solutions, top_solutions_ids)


	# TODO: Check to other classes
	solutions.sort(reverse=True, key=lambda i: i['CreatedAt'])
	last_solutions = solutions[0:LAST_SOLUTIONS_AMOUNT]
	last_solutions_ids = [solution['Id'] for solution in solutions]


	# Compose all solutions ids
	solutions_ids = priority_solutions_ids
	solutions_ids.extend(top_solutions_ids)
	solutions_ids.extend(last_solutions_ids)

	return solutions_ids # TODO: add users_ids and solutions


if __name__ != '__main__':
	sys.modules[__name__] = main
