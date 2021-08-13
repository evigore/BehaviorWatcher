import datetime

SUSPECT_AMOUNT = 30
FACULTY_RATIO = 0.8
REPUTATION_RATIO = 0.1
MOST_RECENT_RATIO = 0.1


FACULTY_AMOUNT = round(SUSPECT_AMOUNT * FACULTY_RATIO)
REPUTATION_AMOUNT = round(SUSPECT_AMOUNT * REPUTATION_RATIO)
MOST_RECENT_AMOUNT = round(SUSPECT_AMOUNT * MOST_RECENT_RATIO)



def filter_users(target, users):
    filtered_users = [user for user in users
        if user['test_passed']
        if target['university_id'] == user['university_id']
        if target['faculty_id'] == user['faculty_id']
        if target['language_id'] == user['language_id']
        if target['course_year'] <= user['course_year']
    ]
    return filtered_users


def remove_user(target, users):
    for user in users:
        if target['id'] == user['id']:
            users.remove(user)

def remove_helpers(target_stole_from_list, users):
    helpers = []
    for user in users:
        if user['id'] in target_stole_from_list:
            helpers.append(user)
    for user in helpers:
        remove_user(user, users)

def add_priority(target, users):
    for user in users:
        priority = 4
        if target['course_year'] == user['course_year']:
            priority += 5
        priority -= user['course_year']
        user['priority'] = priority


def select_most_recent_users(users):
    most_recent_users = []
    users.sort(reverse=False, 
        key=lambda user: datetime.date.fromisoformat(user['last_login_time'])
    )
    most_recent_users.extend(users[:MOST_RECENT_AMOUNT])
    for user in most_recent_users:
        remove_usert(user, users)
    return most_recent_users


def select_users_by_reputation(users):
    pass
