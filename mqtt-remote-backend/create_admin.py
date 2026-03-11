from app import create_app
from app.models import db, User

app = create_app()

with app.app_context():
    db.create_all()
    
    admin = User.query.filter_by(username='admin').first()
    if admin:
        if not admin.is_admin:
            admin.is_admin = True
            db.session.commit()
            print('User "admin" is already exists, updated to admin role.')
        else:
            print('Admin user "admin" already exists.')
    else:
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully!')
    
    print('\nAdmin credentials:')
    print('Username: admin')
    print('Password: admin123')
    print('Please change the password after first login!')
