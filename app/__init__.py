from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.routes import bp
    app.register_blueprint(bp)

    # Add CLI command to recreate database
    @app.cli.command("recreate-db")
    def recreate_db():
        """Recreates the database. WARNING: This will delete all data!"""
        db.drop_all()
        db.create_all()
        print("Database recreated!")

    return app