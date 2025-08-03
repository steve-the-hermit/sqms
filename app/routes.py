from flask import Blueprint, render_template, redirect, request, session, flash, make_response, current_app
from app.models import db, Patient, Queue, Log, Receipt, Doctor
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pandas as pd
import io
from flask import send_file
from flask import url_for
from io import BytesIO
from reportlab.pdfgen import canvas
from app.simulation import start_simulation_logic, stop_simulation_logic
import time

main = Blueprint('main', __name__)

@main.route('/')
def homepage():
    queue = (
        db.session.query(Queue, Patient, Doctor)
        .join(Patient, Queue.patient_id == Patient.patient_id)
        .outerjoin(Doctor, Queue.doctor_id == Doctor.id)
        .filter(Queue.served == False)
        .order_by(Queue.arrival_time)
        .all()
    )
    return render_template('home.html', queue=queue)

@main.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        patient_id = request.form['patient_id']
        name = request.form['name']
        phone = request.form['phone']
        category = request.form['category'] 

        patient = Patient(patient_id=patient_id, name=name, phone=phone, category=category)
        db.session.add(patient)
        db.session.commit()

        # Assign doctor
        least_busy_doctor = (
            db.session.query(Doctor)
            .outerjoin(Queue, (Doctor.id == Queue.doctor_id) & (Queue.served == False))
            .group_by(Doctor.id)
            .order_by(db.func.count(Queue.queue_id))
            .first()
        )

        doctor_id = least_busy_doctor.id if least_busy_doctor else None
        queue_entry = Queue(patient_id=patient_id, doctor_id=doctor_id)
        db.session.add(queue_entry)

        receipt = Receipt(
    receipt_id=f"R{int(time.time() * 1000)}",  
    patient_id=patient_id,
    doctor_id=doctor_id
)

        db.session.add(receipt)

        log = Log(
    action='Patient checked in',
    patient_id=patient_id,
    doctor_id=doctor_id  # <-- Add this
)

        db.session.add(log)

        db.session.commit()

        return render_template('receipt.html',receipt=receipt, patient=patient, doctor=least_busy_doctor)
    return render_template('checkin.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            return redirect('/dashboard')
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect('/login')

    search = request.args.get('search', '').lower()
    doctor_filter = request.args.get('doctor')
    status_filter = request.args.get('status')

    queue_query = (
        db.session.query(Queue, Patient, Doctor)
        .join(Patient, Queue.patient_id == Patient.patient_id)
        .outerjoin(Doctor, Queue.doctor_id == Doctor.id)
        .order_by(Queue.arrival_time)
    )

    if search:
        queue_query = queue_query.filter(
            (Patient.name.ilike(f"%{search}%")) |
            (Patient.patient_id.ilike(f"%{search}%"))
        )

    if doctor_filter:
        queue_query = queue_query.filter(Doctor.name == doctor_filter)

    if status_filter == 'waiting':
        queue_query = queue_query.filter(Queue.served == False)
    elif status_filter == 'served':
        queue_query = queue_query.filter(Queue.served == True)

    queue = queue_query.all()
    doctor_list = Doctor.query.all()

    return render_template('dashboard.html', queue=queue, doctor_list=doctor_list)


@main.route('/serve/<int:queue_id>', methods=['POST'])
def serve_patient(queue_id):
    if not session.get('admin_logged_in'):
        return redirect('/login')

    queue = Queue.query.get(queue_id)
    if queue:
        queue.served = True
        log = Log(
         action='Patient served',
        patient_id=queue.patient_id,
        doctor_id=queue.doctor_id
)

        doctor = Doctor.query.get(queue.doctor_id)
        if doctor:
            doctor.is_available = True
        db.session.add(log)
        db.session.commit()
        flash('Patient served successfully.', 'success')
    else:
        flash('Queue entry not found.', 'danger')

    return redirect('/dashboard')



@main.route('/doctor/serve/<int:queue_id>', methods=['POST'])
def doctor_serve_patient(queue_id):
    doctor_id = session.get('doctor_id')
    if not doctor_id:
        return redirect('/doctor/login')

    queue = Queue.query.get(queue_id)
    if queue and queue.doctor_id == doctor_id:
        queue.served = True
        doctor = Doctor.query.get(doctor_id)
        if doctor:
            doctor.is_available = True
        log = Log(
    action='Patient served',
    patient_id=queue.patient_id,
    doctor_id=queue.doctor_id
)

        db.session.add(log)
        db.session.commit()
        flash('Patient served successfully.', 'success')
    else:
        flash('Invalid access or queue entry not found.', 'danger')

    return redirect('/doctor/dashboard')

@main.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@main.route('/logs')
def view_logs():
    if not session.get('admin_logged_in'):
        return redirect('/login')
    
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    return render_template('logs.html', logs=logs)

@main.route('/doctor/login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        doctor = Doctor.query.filter_by(username=username).first()
        if doctor and check_password_hash(doctor.password_hash, password):
            session['doctor_id'] = doctor.id
            flash('Login successful!', 'success')
            return redirect(f'/doctor/dashboard/{doctor.id}')
        flash('Invalid credentials', 'danger')
    return render_template('doctor_login.html')

@main.route('/doctor/dashboard/<int:doctor_id>')
def doctor_dashboard(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        flash('Doctor not found.', 'danger')
        return redirect('/doctor/login')

    queue = Queue.query.filter_by(doctor_id=doctor_id, served=False).order_by(Queue.arrival_time).all()

    return render_template('doctor_dashboard.html', doctor=doctor, queue=queue)



@main.route('/export/excel')
def export_logs_excel():
    logs = (
        db.session.query(Log, Patient.name.label('patient_name'), Doctor.name.label('doctor_name'))
        .outerjoin(Patient, Log.patient_id == Patient.patient_id)
        .outerjoin(Doctor, Log.doctor_id == Doctor.id)
        .order_by(Log.timestamp.desc())
        .all()
    )

    data = []
    for log, patient_name, doctor_name in logs:
        data.append({
            "Timestamp": log.timestamp,
            "Action": log.action,
            "Doctor": Doctor.query.get(log.doctor_id).name if log.doctor_id else "N/A",
            "Patient ID": log.patient_id,
            "Patient Name": patient_name or 'N/A',
            "Doctor Name": doctor_name or 'N/A',
            "Details": log.details or ''
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Logs')

    output.seek(0)

    return send_file(
        output,
        download_name="logs.xlsx",
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@main.route('/print_receipt/<int:receipt_id>/')
def print_receipt(receipt_id):
    receipt = Receipt.query.get_or_404(receipt_id)
    return render_template('printable_receipt.html', receipt=receipt)

@main.route('/doctor/logout')
def doctor_logout():
    session.pop('doctor_logged_in', None)
    session.pop('doctor_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.doctor_login'))

@main.route('/export/pdf')
def export_logs_pdf():
    logs = Log.query.all()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setTitle("Logs Export")

    pdf.drawString(100, 800, "Smart Queue Logs Report")

    y = 760
    for log in logs:
        log_line = f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {log.action} - {log.details}"
        pdf.drawString(40, y, log_line)
        y -= 20
        if y < 40:
            pdf.showPage()
            y = 800

    pdf.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="logs_report.pdf", mimetype='application/pdf')

@main.route('/reset_logs', methods=['POST'])
def reset_logs():
    Log.query.delete()
    db.session.commit()
    flash("All logs have been cleared.")
    return redirect(url_for('main.view_logs'))

@main.route('/simulate/start', methods=['POST'])
def start_simulation():
    app = current_app._get_current_object()  # 👈 this unwraps the proxy into the real app
    start_simulation_logic(app)
    return redirect(url_for('main.dashboard'))

@main.route('/simulate/stop', methods=['GET'])
def stop_simulation():
    stop_simulation_logic()
    return redirect(url_for('main.dashboard'))

