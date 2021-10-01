import connexion
import os
import Thirdparty

connex_app = connexion.FlaskApp(__name__, specification_dir='./')
app = connex_app.app

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///behaviorWatcher.db'
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

Thirdparty.db.init_app(app)
Thirdparty.ma.init_app(app)

connex_app.add_api('./swagger.yaml')

with app.app_context():
    if not os.path.exists("behaviorWatcher.db"):
        Thirdparty.db.create_all()

connex_app.run(debug=False)
