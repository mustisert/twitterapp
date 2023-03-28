from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate


# Datenbank-Instanz erstellen
db = SQLAlchemy()
login_manager = LoginManager()

# Funktion zum Erstellen einer Flask-App
def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secretkey"
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://twitterappuser:twitterapppassword@mysql:3306/twitterappdb"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Datenbank und Login-Manager mit App initialisieren
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    login_manager.login_view = 'main.login'
    
# Datenbanktabellen erstellen, falls sie noch nicht existieren
    with app.app_context():
        db.create_all()

    from app.routes import main

    app.register_blueprint(main)
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    return app