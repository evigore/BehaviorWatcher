import connexion
import os
from db import db
from flask_marshmallow import Marshmallow

connex_app = connexion.FlaskApp(__name__, specification_dir='./')
app = connex_app.app

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///behaviorWatcher.db'
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

ma = Marshmallow()

db.init_app(app)
ma.init_app(app)

with app.app_context():
	if not os.path.exists("behaviorWatcher.db"):
		db.create_all()
