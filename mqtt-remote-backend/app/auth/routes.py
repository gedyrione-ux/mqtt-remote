from flask import Blueprint, request, jsonify
from app.models import User, db
from app.utils.jwt_utils import create_token

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': '用户名和密码是必填项'}), 400
    
    username = data['username']
    email = data.get('email')
    password = data['password']
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 400
    
    if email and User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已被使用'}), 400
    
    user = User(username=username, email=email)
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '注册失败，请稍后重试'}), 500
    
    return jsonify({
        'message': '注册成功',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'username_or_email' not in data or 'password' not in data:
        return jsonify({'error': '请提供用户名/邮箱和密码'}), 400
    
    username_or_email = data['username_or_email']
    password = data['password']
    
    user = User.query.filter_by(username=username_or_email).first()
    if not user:
        user = User.query.filter_by(email=username_or_email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': '用户名/邮箱或密码错误'}), 401
    
    access_token = create_token(user.id)
    
    return jsonify({
        'message': '登录成功',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        }
    }), 200
