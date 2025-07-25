from .models import db, Log

def log_action(action, patient_id=None, actor=None):
    new_log = Log(action=action, patient_id=patient_id, actor=actor)
    db.session.add(new_log)
    db.session.commit()
