import os
import connexion
import thirdparty

connex_app = connexion.FlaskApp(__name__, specification_dir='./')
app = connex_app.app

# Configure the SqlAlchemy part of the app instance
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///behaviorWatcher.db'
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

thirdparty.db.init_app(app)
thirdparty.ma.init_app(app)

connex_app.add_api('./swagger.yaml')

with app.app_context():
    if not os.path.exists("behaviorWatcher.db"):
        thirdparty.db.create_all()

connex_app.run(debug=False)
