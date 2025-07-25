from datetime import datetime
from . import db

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    actor = db.Column(db.String(100)) 
    patient_id = db.Column(db.String(100), db.ForeignKey('patients.patient_id'))

    def __repr__(self):
        return f"<Log {self.action} @ {self.timestamp}>"


class Doctor(db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_available = db.Column(db.Boolean, default=True)

class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.Enum('emergency', 'on_time', 'early', 'late', 'walk_in'), nullable=False)
    registered_at = db.Column(db.DateTime, server_default=db.func.now())

class Receipt(db.Model):
    __tablename__ = 'receipts'
    receipt_id = db.Column(db.String(200), primary_key=True)
    patient_id = db.Column(db.String(100), db.ForeignKey('patients.patient_id'))
    issue_time = db.Column(db.DateTime, server_default=db.func.now())
    estimated_wait = db.Column(db.Integer)

class Queue(db.Model):
    __tablename__ = 'queue'
    queue_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(100), db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=True)
    priority_level = db.Column(db.Integer)
    arrival_time = db.Column(db.DateTime, server_default=db.func.now())
    session_end_time = db.Column(db.DateTime, nullable=True)
    served = db.Column(db.Boolean, default=False)
