from generator import *
from datetime import date

SUSPECT_AMOUNT = 30
FACULTY_RATIO = 0.7
REPUTATION_RATIO = 0.3

FACULTY_AMOUNT = round(SUSPECT_AMOUNT * FACULTY_RATIO)
REPUTATION_AMOUNT = round(SUSPECT_AMOUNT * REPUTATION_RATIO)

# save_users_to_file("users", generate_users())

def filter_users(target, users):
    filtered_users = [user for user in users
        if user['test_passed']
        if target['language_id'] == user['language_id']
        if target['course_year'] <= user['course_year']
    ]
    return filtered_users


def remove_user(target, users):
    for user in users:
        if target['id'] == user['id']:
            users.remove(user)

def find_helpers(target_stole_from_list):
    helpers = []
    for user in users:
        if user['id'] in target_stole_from_list:
            helpers.append(user)
    return helpers


def add_priority(target, users):
    for user in users:
        priority = 4
        if target['university_id'] == user['university_id']:
            priority += 100
        if target['faculty_id'] == user['faculty_id']:
            priority += 10
        if target['course_year'] == user['course_year']:
            priority += 5
        priority -= user['course_year']
        user['priority'] = priority




users = load_users_from_file("users")
target = users[1]
users.remove(target)


users = filter_users(target, users)
add_priority(target, users)

# Remove target['stole_from'] users
helpers = find_helpers(target['stole_from'])
for user in helpers:
    remove_user(user, users)


# Sort by priority descending
users.sort(key=lambda user: user['priority'], reverse=True)
faculty_users = users[:FACULTY_AMOUNT]
for user in faculty_users:
    remove_user(user, users)


# Sort by reputation descending
users.sort(key=lambda user: user['reputation'], reverse=True)
reputation_users = users[:REPUTATION_AMOUNT]
for user in reputation_users:
    remove_user(user, users)


suspected_users = []
suspected_users.extend(faculty_users, reputation_users)

