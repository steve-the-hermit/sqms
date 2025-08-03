from app import create_app, db
from app.models import Doctor
from werkzeug.security import generate_password_hash

app = create_app()

doctors = [
    "Dr. Smith",
    "Dr. Achieng",
    "Dr. Patel",
    "Dr. House",
    "Dr. Watson",
    "Dr. Grey",
    "Dr. Strange",
    "Dr. Who",
    "Dr. Karaba",
    "Dr. Davison"
]

with app.app_context():
    for i, name in enumerate(doctors, start=1):
        username = f"doctor{i}"
        password = generate_password_hash("doctor123")
        doctor = Doctor(
            name=name,
            is_available=True,
            specialization=None,
            username=username,
            password_hash=password
        )
        db.session.add(doctor)

    db.session.commit()
    print("Doctors seeded successfully, Hermit-san.")
