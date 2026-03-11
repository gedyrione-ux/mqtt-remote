from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Device, db

devices_bp = Blueprint('devices', __name__, url_prefix='/api/devices')

@devices_bp.route('', methods=['GET'])
@jwt_required()
def get_devices():
    user_id = get_jwt_identity()
    devices = Device.query.filter_by(user_id=user_id).all()
    return jsonify([device.to_dict() for device in devices]), 200

@devices_bp.route('/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device(device_id):
    user_id = get_jwt_identity()
    device = Device.query.get(device_id)
    
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    if device.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(device.to_dict()), 200
