from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    devices = db.relationship('Device', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_id = db.Column(db.String(50), unique=True, nullable=False)
    device_name = db.Column(db.String(100), nullable=True)
    device_username = db.Column(db.String(80), nullable=False)
    device_password = db.Column(db.String(255), nullable=False)
    publish_topic = db.Column(db.String(255), nullable=False)
    subscribe_topic = db.Column(db.String(255), nullable=False)
    device_code = db.Column(db.Integer, default=68, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'device_name': self.device_name,
            'device_username': self.device_username,
            'device_password': self.device_password,
            'publish_topic': self.publish_topic,
            'subscribe_topic': self.subscribe_topic,
            'device_code': self.device_code,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
