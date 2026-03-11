from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models import Device, User, db
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/devices', methods=['GET'])
@admin_required
def get_all_devices():
    user_id = request.args.get('user_id')
    query = Device.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    devices = query.all()
    result = []
    for device in devices:
        device_dict = device.to_dict()
        device_dict['username'] = device.user.username
        result.append(device_dict)
    
    return jsonify(result), 200

@admin_bp.route('/devices', methods=['POST'])
@admin_required
def create_device():
    data = request.get_json()
    
    required_fields = ['user_id', 'device_id', 'device_username', 'device_password', 'publish_topic', 'subscribe_topic']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    user = User.query.get(data['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    existing_device = Device.query.filter_by(device_id=data['device_id']).first()
    if existing_device:
        return jsonify({'error': 'Device ID already exists'}), 400
    
    device = Device(
        user_id=data['user_id'],
        device_id=data['device_id'],
        device_name=data.get('device_name'),
        device_username=data['device_username'],
        device_password=data['device_password'],
        publish_topic=data['publish_topic'],
        subscribe_topic=data['subscribe_topic'],
        device_code=data.get('device_code', 68)
    )
    
    try:
        db.session.add(device)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create device'}), 500
    
    return jsonify(device.to_dict()), 201

@admin_bp.route('/devices/<int:device_id>', methods=['PUT'])
@admin_required
def update_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    data = request.get_json()
    
    if 'user_id' in data:
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        device.user_id = data['user_id']
    
    if 'device_id' in data:
        existing_device = Device.query.filter(
            Device.device_id == data['device_id'],
            Device.id != device_id
        ).first()
        if existing_device:
            return jsonify({'error': 'Device ID already exists'}), 400
        device.device_id = data['device_id']
    
    if 'device_name' in data:
        device.device_name = data['device_name']
    if 'device_username' in data:
        device.device_username = data['device_username']
    if 'device_password' in data:
        device.device_password = data['device_password']
    if 'publish_topic' in data:
        device.publish_topic = data['publish_topic']
    if 'subscribe_topic' in data:
        device.subscribe_topic = data['subscribe_topic']
    if 'device_code' in data:
        device.device_code = data['device_code']
    
    device.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update device'}), 500
    
    return jsonify(device.to_dict()), 200

@admin_bp.route('/devices/<int:device_id>', methods=['DELETE'])
@admin_required
def delete_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    try:
        db.session.delete(device)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete device'}), 500
    
    return jsonify({'message': 'Device deleted successfully'}), 200
