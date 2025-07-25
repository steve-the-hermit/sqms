from flask import Blueprint, request, render_template, redirect, session, flash, make_response, send_file, current_app, url_for
from .models import db, Patient, Receipt, Queue, Doctor, Log
from .simulation import start_simulation, stop_simulation
import time, io, pandas as pd
from fpdf import FPDF

main = Blueprint('main', __name__)

@main.route('/')
def homepage():
    queue_entries = (
        db.session.query(Queue, Patient, Doctor)
        .join(Patient, Queue.patient_id == Patient.patient_id)
        .outerjoin(Doctor, Queue.doctor_id == Doctor.doctor_id)
        .filter(Queue.served == False)
        .order_by(Queue.arrival_time)
        .all()
    )

    receipts = {
        r.patient_id: r for r in Receipt.query.order_by(Receipt.issue_time.desc()).all()
    }

    return render_template('home.html', queue_data=queue_entries, receipts=receipts)



@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == current_app.config['ADMIN_USERNAME'] and password == current_app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            flash('Login successful', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')


@main.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('main.login'))


@main.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        pid = request.form['patient_id']
        name = request.form['name']
        cat = request.form['category']

        wait = {'emergency': 0, 'on_time': 10, 'early': 20, 'late': 30, 'walk_in': 40}
        priority = {'emergency': 1, 'on_time': 2, 'early': 3, 'late': 4, 'walk_in': 4}

        patient = Patient.query.get(pid)
        if not patient:
            patient = Patient(patient_id=pid, name=name, category=cat)
            db.session.add(patient)
        else:
            patient.name = name
            patient.category = cat

        rid = f"R{int(time.time() * 1000)}"
        receipt = Receipt(receipt_id=rid, patient_id=pid, estimated_wait=wait.get(cat, 45))

        # === Least Busy Doctor Logic ===
        doctors = Doctor.query.filter_by(is_available=True).all()
        doctor_loads = {
            doctor.doctor_id: Queue.query.filter_by(doctor_id=doctor.doctor_id, served=False).count()
            for doctor in doctors
        }

        assigned_doctor_id = min(doctor_loads, key=doctor_loads.get) if doctor_loads else None
        assigned_doctor = Doctor.query.get(assigned_doctor_id) if assigned_doctor_id else None

        if assigned_doctor:
            assigned_doctor.is_available = False  # Optional: toggle if doctor should only take one at a time

        queue = Queue(
            patient_id=pid,
            doctor_id=assigned_doctor.doctor_id if assigned_doctor else None,
            priority_level=priority.get(cat, 5)
        )

        db.session.add_all([receipt, queue, Log(action='Checked in', patient_id=pid)])
        db.session.commit()

        return redirect(f"/?receipt_id={rid}")

    return render_template('checkin.html')



@main.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        flash("Please log in as admin to access the dashboard.", "warning")
        return redirect(url_for('main.login'))

    status = request.args.get('status')
    doctor_name = request.args.get('doctor')
    search_term = request.args.get('search', '')
    query = db.session.query(Queue, Patient, Doctor).join(Patient).outerjoin(Doctor)
    if status == 'served': query = query.filter(Queue.served == True)
    elif status == 'waiting': query = query.filter(Queue.served == False)
    if doctor_name: query = query.filter(Doctor.name.ilike(f"%{doctor_name}%"))
    if search_term:
        query = query.filter((Patient.patient_id.ilike(f"%{search_term}%")) | (Patient.name.ilike(f"%{search_term}%")))
    queue_data = query.order_by(Queue.priority_level, Queue.arrival_time).all()
    doctors = Doctor.query.order_by(Doctor.name).all()
    return render_template('dashboard.html', queue_data=queue_data, doctor_list=doctors)


@main.route('/logs')
def view_logs():
    if not session.get('admin_logged_in'):
        flash("Admin login required to access logs.", "warning")
        return redirect(url_for('main.login'))
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    return render_template('logs.html', logs=logs)


@main.route('/logs/export/excel')
def export_logs_excel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.login'))
    logs = Log.query.all()
    data = [{'Timestamp': log.timestamp, 'Action': log.action, 'Patient ID': log.patient_id} for log in logs]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name='logs.xlsx', as_attachment=True)


@main.route('/logs/export/pdf')
def export_logs_pdf():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.login'))
    logs = Log.query.all()
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="System Logs", ln=True, align='C'); pdf.ln(10)
    for log in logs:
        pdf.multi_cell(0, 10, txt=f"{log.timestamp} - {log.action} - Patient ID: {log.patient_id}")
    output = io.BytesIO(); pdf.output(output); output.seek(0)
    return send_file(output, download_name='logs.pdf', as_attachment=True)

@main.route('/logs/reset', methods=['POST'])
def reset_logs():
    if not session.get('admin_logged_in'):
        return redirect('/login')
    
    Log.query.delete()
    db.session.commit()
    return redirect('/logs')

@main.route('/simulate/start', methods=['POST'])
def start_sim():
    if not session.get('admin_logged_in'):
        return redirect('/login')
    start_simulation(current_app._get_current_object())
    flash("Simulation started", "success")
    return redirect('/dashboard')

@main.route('/simulate/stop', methods=['POST'])
def stop_sim():
    if not session.get('admin_logged_in'):
        return redirect('/login')
    stop_simulation()
    flash("Simulation stopped", "info")
    return redirect('/dashboard')

@main.route('/serve/<int:queue_id>', methods=['POST'])
def serve_patient(queue_id):
    if not session.get('admin_logged_in'):
        return redirect('/login')

    queue = Queue.query.get(queue_id)
    if queue:
        queue.served = True
        log = Log(action='Patient served', patient_id=queue.patient_id)
        doctor = Doctor.query.get(queue.doctor_id)
        if doctor:
            doctor.is_available = True
        db.session.add(log)
        db.session.commit()
        flash('Patient served successfully.', 'success')
    else:
        flash('Queue entry not found.', 'danger')

    return redirect('/dashboard')
