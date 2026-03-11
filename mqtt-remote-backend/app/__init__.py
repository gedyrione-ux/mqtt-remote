from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app.config import Config
from app.models import db
from app.auth.routes import auth_bp
from app.devices.routes import devices_bp
from app.admin.routes import admin_bp

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(admin_bp)
    
    return app
