from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import exc, or_, and_

db = SQLAlchemy()
ma = Marshmallow()
