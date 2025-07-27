from faker import Faker
import threading
import time
import random
from datetime import datetime, timedelta
from .models import db, Patient, Receipt, Queue, Doctor, Log

fake = Faker()
simulating = False
sim_thread = None

def auto_simulate(app):
    global simulating
    with app.app_context():
        while simulating:
            patient_id = f"SIM-{int(time.time() * 1000)}"
            name = fake.name()
            categories = ['emergency', 'on_time', 'early', 'late', 'walk_in']
            category = random.choice(categories)

            wait_times = {
                'emergency': 0, 'on_time': 10, 'early': 20,
                'late': 30, 'walk_in': 40
            }
            priorities = {
                'emergency': 1, 'on_time': 2, 'early': 3,
                'late': 4, 'walk_in': 4
            }

            patient = Patient(patient_id=patient_id, name=name, category=category)
            receipt = Receipt(
                receipt_id=f"R{int(time.time() * 1000)}",
                patient_id=patient_id,
                estimated_wait=wait_times[category]
            )

            doctor = Doctor.query.filter_by(is_available=True).first()
            if doctor:
                doctor_id =Doctor.id
                doctor.is_available = False
                session_duration = random.randint(10, 30)
                session_end = datetime.utcnow() + timedelta(seconds=session_duration)
            else:
                doctor_id = None
                session_end = None
                print("⚠️ No doctor available. Patient unassigned.")

            queue = Queue(
                patient_id=patient_id,
                doctor_id=doctor_id,
                priority_level=priorities[category],
                session_end_time=session_end
            )

            db.session.add(patient)
            db.session.flush() 
            db.session.add(receipt)
            db.session.add(queue)
            db.session.add(Log(action="Auto Check-in", patient_id=patient_id))

            db.session.commit()

            now = datetime.utcnow()
            ready_to_serve = Queue.query.filter(
                Queue.served == False,
                Queue.doctor_id != None,
                Queue.session_end_time != None,
                Queue.session_end_time <= now
            ).all()

            for item in ready_to_serve:
                item.served = True
                if item.doctor_id:
                    doc = Doctor.query.get(item.doctor_id)
                    doc.is_available = True
                db.session.add(Log(action="Auto Served", patient_id=item.patient_id))

            db.session.commit()

            unassigned = Queue.query.filter_by(served=False, doctor_id=None).all()
            for unq in unassigned:
                available_doc = Doctor.query.filter_by(is_available=True).first()
                if available_doc:
                    unq.doctor_id = available_doc.doctor_id
                    available_doc.is_available = False
                    unq.session_end_time = datetime.utcnow() + timedelta(seconds=random.randint(10, 30))
                    db.session.add(Log(action="Reassigned Doctor", patient_id=unq.patient_id))
                else:
                    break 

            db.session.commit()
            time.sleep(10)
def start_simulation(app):
    global simulating, sim_thread
    if not simulating:
        simulating = True
        sim_thread = threading.Thread(target=auto_simulate, args=(app,))
        sim_thread.daemon = True
        sim_thread.start()

def stop_simulation():
    global simulating
    simulating = False


def init_app(app):
    with app.app_context():
     print("🧠 Simulation module ready.")
