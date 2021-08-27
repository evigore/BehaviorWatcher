import connexion
import os
from thirdparty import db, ma
import api

connex_app = connexion.FlaskApp(__name__, specification_dir='./')
app = connex_app.app

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///behaviorWatcher.db'
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)
ma.init_app(app)

connex_app.add_api('./api/swagger.yaml')  # uses ./api/swagger.yaml

with app.app_context():
	if not os.path.exists("behaviorWatcher.db"):
		db.create_all()

connex_app.run(debug=True)
