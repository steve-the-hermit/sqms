from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class Log(db.Model):
    __tablename__ = 'log'

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    patient_id = db.Column(db.String(100), db.ForeignKey('patients.patient_id'), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    details = db.Column(db.Text)


    details = db.Column(db.Text, nullable=True)




class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(64), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    specialization = db.Column(db.String(64), nullable=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Patient(db.Model):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    patient_id = db.Column(db.String(100))  
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    category = db.Column(db.Enum('emergency', 'on_time', 'early', 'late', 'walk_in'), nullable=False)
    registered_at = db.Column(db.DateTime, server_default=db.func.now())


class Receipt(db.Model):
    __tablename__ = 'receipts'

    receipt_id = db.Column(db.String(100), primary_key=True)
    patient_id = db.Column(db.String(100), db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    estimated_wait = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=db.func.now())  


class Queue(db.Model):
    __tablename__ = 'queue'
    queue_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(100), db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    priority_level = db.Column(db.Integer)
    arrival_time = db.Column(db.DateTime, server_default=db.func.now())
    session_end_time = db.Column(db.DateTime, nullable=True)
    served = db.Column(db.Boolean, default=False)
