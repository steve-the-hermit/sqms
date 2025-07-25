from app import create_app, db
from app.models import Doctor

app = create_app()

with app.app_context():
    db.session.add_all([ 
        Doctor(name='Dr. Smith', is_available=True),
        Doctor(name='Dr. Achieng', is_available=True),
        Doctor(name='Dr. Patel', is_available=True),
        Doctor(name='Dr. House', is_available=True),
        Doctor(name='Dr. Watson', is_available=True),
        Doctor(name='Dr. Grey', is_available=True),
        Doctor(name='Dr. Strange', is_available=True),
        Doctor(name='Dr. Who', is_available=True),
        Doctor(name='Dr. Karaba', is_available=True),
        Doctor(name='Dr. Davison', is_available=True)
    ])
    
    db.session.commit()
    print("Sample doctors added!")
