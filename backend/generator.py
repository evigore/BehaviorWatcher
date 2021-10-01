import random
import json
from datetime import date


def generate_users():
    random.seed(1234)
    users = []

    for i in range(5000):
        user = {
            'id': i,
            'task_id': random.randrange(3),
            'language_id': random.randrange(0, 3),
            'sending_task_time': date(year=2021 - random.randrange(2), month=8 - random.randrange(2),
                                      day=1 + random.randrange(25)),
            'test_passed': bool(random.randrange(2)),
            'stole_from': [random.randrange(1000) for i in range(random.randrange(4))],
            'reputation': int(random.random() * 100),
            'course_year': random.randrange(4) + 1,
            'faculty_id': random.randrange(3),
            'university_id': random.randrange(3)
        }

        users.append(user)

    return users


def save_users_to_file(filename, users):
    f = open(filename + '.json', 'w')
    f.write(json.dumps(users, indent=4, sort_keys=True, default=str))
    f.close()


def load_users_from_file(filename):
    f = open(filename + '.json', 'r')
    users = json.load(f)
    f.close()

    return users
