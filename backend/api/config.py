import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

connex_app = connexion.FlaskApp(__name__, specification_dir='./')
app = connex_app.app

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite///behaviorWatcher.db'
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create the SqlAlchemy db instance
db = SQLAlchemy(app)

# [REQUIRED] initialize after db
ma = Marshmallow(app)
