from datetime import datetime
from flask import Blueprint, request, jsonify
from app.models import Device, User, db
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# ==================== 操作员管理 API ====================

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """获取所有操作员列表 (is_admin=0)"""
    users = User.query.filter_by(is_admin=False).all()
    result = []
    for user in users:
        user_dict = user.to_dict()
        result.append(user_dict)
    return jsonify(result), 200

@admin_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """新增操作员账号（自动哈希加密密码）"""
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': '用户名和密码是必填项'}), 400
    
    username = data['username']
    password = data['password']
    email = data.get('email')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    if email and User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已被使用'}), 400
    
    user = User(username=username, email=email, is_admin=False)
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '创建用户失败，请稍后重试'}), 500
    
    return jsonify(user.to_dict()), 201

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """删除操作员（同步将其名下设备的 user_id 置为 null 或分配给默认管理员）"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    # 查找是否有默认管理员（is_admin=True 的第一个用户）
    default_admin = User.query.filter_by(is_admin=True).first()
    
    # 将该用户名下的设备重新分配给默认管理员，或设为 None
    devices = Device.query.filter_by(user_id=user_id).all()
    for device in devices:
        if default_admin:
            device.user_id = default_admin.id
        else:
            device.user_id = None
    
    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除用户失败，请稍后重试'}), 500
    
    return jsonify({'message': '用户删除成功'}), 200

# ==================== 车辆装备库 API ====================

@admin_bp.route('/devices', methods=['GET'])
@admin_required
def get_all_devices():
    """获取所有车辆列表，并使用 JOIN 附带查出该车辆所属的操作员姓名"""
    query = Device.query
    devices = query.all()
    result = []
    for device in devices:
        device_dict = device.to_dict()
        device_dict['owner_name'] = device.user.username if device.user else None
        device_dict['owner_id'] = device.user_id
        result.append(device_dict)
    
    return jsonify(result), 200

@admin_bp.route('/devices', methods=['POST'])
@admin_required
def create_device():
    """录入新抑尘车（管理员需输入车号 device_id、真实硬件地址码 device_code）"""
    data = request.get_json()
    
    required_fields = ['device_id', 'device_username', 'device_password', 'publish_topic', 'subscribe_topic']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} 是必填项'}), 400
    
    user_id = data.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 404
    else:
        # 如果没有指定 user_id，分配给第一个管理员
        default_admin = User.query.filter_by(is_admin=True).first()
        if not default_admin:
            return jsonify({'error': '没有找到默认管理员'}), 400
        user_id = default_admin.id
    
    existing_device = Device.query.filter_by(device_id=data['device_id']).first()
    if existing_device:
        return jsonify({'error': '车号已存在'}), 400
    
    device = Device(
        user_id=user_id,
        device_id=data['device_id'],
        device_name=data.get('device_name'),
        device_username=data['device_username'],
        device_password=data['device_password'],
        publish_topic=data['publish_topic'],
        subscribe_topic=data['subscribe_topic'],
        device_code=data.get('device_code', 2)
    )
    
    try:
        db.session.add(device)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '创建设备失败'}), 500
    
    result = device.to_dict()
    result['owner_name'] = device.user.username
    
    return jsonify(result), 201

@admin_bp.route('/devices/<int:device_id>', methods=['PUT'])
@admin_required
def update_device(device_id):
    """修改车辆信息，最重要的是能够重新分配操作员"""
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': '设备不存在'}), 404
    
    data = request.get_json()
    
    if 'user_id' in data:
        if data['user_id']:
            user = User.query.get(data['user_id'])
            if not user:
                return jsonify({'error': '用户不存在'}), 404
            device.user_id = data['user_id']
        else:
            default_admin = User.query.filter_by(is_admin=True).first()
            if default_admin:
                device.user_id = default_admin.id
    
    if 'device_id' in data:
        existing_device = Device.query.filter(
            Device.device_id == data['device_id'],
            Device.id != device_id
        ).first()
        if existing_device:
            return jsonify({'error': '车号已存在'}), 400
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
        return jsonify({'error': '更新设备失败'}), 500
    
    result = device.to_dict()
    result['owner_name'] = device.user.username if device.user else None
    
    return jsonify(result), 200

@admin_bp.route('/devices/<int:device_id>', methods=['DELETE'])
@admin_required
def delete_device(device_id):
    """报废/删除车辆"""
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': '设备不存在'}), 404
    
    try:
        db.session.delete(device)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '删除设备失败'}), 500
    
    return jsonify({'message': '设备删除成功'}), 200
