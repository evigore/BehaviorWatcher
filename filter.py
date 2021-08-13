from generator import load_users_from_file
from filter_tools import *
import datetime


# Prepare data
users = load_users_from_file("users")
target = users[1]
users.remove(target)
users = filter_users(target, users)
add_priority(target, users)
remove_helpers(target['stole_from'], users)


# Sort by date and select most recent students
most_recent_users = select_most_recent_users(users)

# Sort by reputation and select with least amount


# Select most local students to target by priority




# # Sort by priority descending
# users.sort(key=lambda user: user['priority'], reverse=True)
# faculty_users = users[:FACULTY_AMOUNT]
# for user in faculty_users:
#     remove_user(user, users)


# # Sort by reputation ascending
# users.sort(key=lambda user: user['reputation'])
# reputation_users = users[:REPUTATION_AMOUNT]
# for user in reputation_users:
#     remove_user(user, users)


# suspected_users = []
# suspected_users.extend(faculty_users)
# suspected_users.extend(reputation_users)

