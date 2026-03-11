from app import create_app
from app.models import db, User, Device

app = create_app()

with app.app_context():
    db.create_all()
    
    user = User.query.filter_by(username='testuser').first()
    if not user:
        user = User(username='testuser', email='testuser@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        print('Created test user: testuser')
    
    existing_device = Device.query.filter_by(device_id='DEV001').first()
    if not existing_device:
        device1 = Device(
            user_id=user.id,
            device_id='DEV001',
            device_name='客厅空调',
            device_username='mqtt_user',
            device_password='mqtt_pass123',
            publish_topic='devices/DEV001/cmd',
            subscribe_topic='devices/DEV001/status',
            device_code=68
        )
        db.session.add(device1)
        
        device2 = Device(
            user_id=user.id,
            device_id='DEV002',
            device_name='卧室电视',
            device_username='mqtt_user',
            device_password='mqtt_pass123',
            publish_topic='devices/DEV002/cmd',
            subscribe_topic='devices/DEV002/status',
            device_code=68
        )
        db.session.add(device2)
        
        db.session.commit()
        print('Created test devices: DEV001 and DEV002')
    else:
        print('Test data already exists')
    
    print('\nTest data setup complete!')
    print('You can login with: username=testuser, password=password123')
