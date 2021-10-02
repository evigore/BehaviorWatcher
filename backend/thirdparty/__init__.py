from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime

db = SQLAlchemy()
ma = Marshmallow()

def fetch(result):
    tmp = []

    for i in result:
        solution = {key: value for key, value in i.items()}
        if 'CreatedAt' in solution:
            solution['CreatedAt'] = datetime.strptime(solution['CreatedAt'].split('.')[0], '%Y-%m-%d %H:%M:%S') # TODO: remove

        tmp.append(solution)

    return tmp
