from app import create_app, db
from app.models import Doctor

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created successfully.")

    if not Doctor.query.first():
        doctors = [
            Doctor(name="Dr. Alice Smith"),
            Doctor(name="Dr. John Doe"),
            Doctor(name="Dr. Maya Patel"),
            Doctor(name="Dr. Kevin Lee"),
            Doctor(name="Dr. Olivia Wang"),
            Doctor(name="Dr. Ethan Kim"),
            Doctor(name="Dr. Clara Zhang"),
            Doctor(name="Dr. Brian Oduor"),
            Doctor(name="Dr. Mercy Njoki"),
            Doctor(name="Dr. Samuel Kibet"),
        ]
        db.session.add_all(doctors)
        db.session.commit()
        print(" Doctors seeded successfully.")
    else:
        print("ℹ Doctors already exist.")
