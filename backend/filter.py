from generator import *
# from filter_tools import *
import datetime


import datetime

SUSPECT_AMOUNT = 30
FACULTY_RATIO = 0.8
REPUTATION_RATIO = 0.1
LAST_SUBMITTERS_RATIO = 0.1


FACULTY_AMOUNT = round(SUSPECT_AMOUNT * FACULTY_RATIO)
REPUTATION_AMOUNT = round(SUSPECT_AMOUNT * REPUTATION_RATIO)
LAST_SUBMITTERS_AMOUNT = round(SUSPECT_AMOUNT * LAST_SUBMITTERS_RATIO)



def filter_users(target, users):
	filtered_users = []

	for user in users:
		if not user['test_passed']:
			continue

		if user['university_id'] != target['university_id']:
			continue

		if user['faculty_id'] != target['faculty_id']:
			continue

		if user['language_id'] != target['language_id']:
			continue

		if user['course_year'] < target['course_year']:
			continue

		filtered_users.append(user)

	return filtered_users


def remove_user_by_id(id, users):
	for user in users:
		if user['id'] == id:
			users.remove(user)

def remove_users_by_id(ids, users):
	ids_to_remove = []
	for user in users:
		if user['id'] in ids:
			ids_to_remove.append(user['id'])

	for id in ids_to_remove:
		remove_user_by_id(id, users)

def add_priority(target, users):
    for user in users:
        priority = 4
        if target['course_year'] == user['course_year']:
            priority += 5
        priority -= user['course_year']
        user['priority'] = priority


def get_last_submitters_since(date, users):
	users.sort(reverse=False, 
		key=lambda user: datetime.date.fromisoformat(user['sending_task_time'])
	)

	start_index = -1
	for i, user in enumerate(users):
		if user['sending_task_time'] <= date:
			start_index = i
			break

	if start_index == -1:
		return []

	last_submitters = users[start_index : start_index+LAST_SUBMITTERS_AMOUNT]
	for user in last_submitters:
		remove_user_by_id(user['id'], users)

	return last_submitters

def get_users_by_reputation(users):
    pass






# Prepare data
users = load_users_from_file("users")
target = users[1]
users.remove(target)
users = filter_users(target, users)
add_priority(target, users)
remove_users_by_id(target['stole_from'], users)


# Sort by date and select last submitters since date
last_submitters = get_last_submitters_since(target['sending_task_time'], users)

# Sort by reputation and select with least amount


# Select most local students to target by priority