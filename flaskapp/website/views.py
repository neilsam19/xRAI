from flask import Blueprint, render_template, request, flash, jsonify, session
from flask_login import login_required, current_user
from .models import Note
from .models import User
from .models import Scan
from . import db
import json
import subprocess  # Import subprocess module
import os  # Import os module for path manipulation
import smtplib
import ast
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from sqlalchemy import desc
from dotenv import load_dotenv, dotenv_values 

load_dotenv() 

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    scan_data = []
    if current_user.isdoctor == 'Yes':
        doctor_scans = db.session.query(Scan, User).filter(Scan.doctoruser_id == current_user.id).join(User, Scan.patientuser_id == User.id).order_by(desc(Scan.date_of_scan)).all()
        # Create a list to store formatted scan data
        for scan, patient in doctor_scans:
            scan_data.append({
                'patient_name': patient.first_name,
                'patient_email': patient.email,
                'scan_name': scan.scan_name,
                'scan_result': scan.scan_result,
                'scan_datetime': scan.date_of_scan.strftime('%Y-%m-%d %H:%M:%S')  # Format datetime
            })
    elif current_user.isdoctor == 'No':
        patient_scans = db.session.query(Scan, User).filter(Scan.patientuser_id == current_user.id).join(User, Scan.doctoruser_id == User.id).order_by(desc(Scan.date_of_scan)).all()
        for scan, doctor in patient_scans:
            scan_data.append({
                'doctor_name': doctor.first_name,
                'doctor_email': doctor.email,
                'scan_name': scan.scan_name,
                'scan_result': scan.scan_result,
                'scan_datetime': scan.date_of_scan.strftime('%Y-%m-%d %H:%M:%S')
            })
    if request.method == 'POST':
        if current_user.isdoctor == 'Yes':
            doctor_scans = db.session.query(Scan, User).filter(Scan.doctoruser_id == current_user.id).join(User, Scan.patientuser_id == User.id).order_by(desc(Scan.date_of_scan)).all()
            # Create a list to store formatted scan data
            for scan, patient in doctor_scans:
                scan_data.append({
                    'patient_name': patient.first_name,
                    'patient_email': patient.email,
                    'scan_name': scan.scan_name,
                    'scan_result': scan.scan_result,
                    'scan_datetime': scan.date_of_scan.strftime('%Y-%m-%d %H:%M:%S')  # Format datetime
                })
                
        form_name = request.form.get('form_name')  # Get the form name from the hidden input
        if form_name == 'imageUploadForm':
            if current_user.isdoctor == 'Yes':
                image = request.files['image']
                if image:
                    image_path = f'website/static/images/{image.filename}'
                    image.save(image_path)
                    image_filename = image.filename  # Store the filename
                    session['image_filename'] = image_filename
                    return render_template("home.html", user=current_user, scan_data=scan_data, image_filename=image_filename)
                
        elif form_name == 'getScan':
            selected_scan = request.form.get("scanType")
            if session.get("image_filename"):
                if selected_scan == 'boneAge':
                    try:
                        image_path = os.path.join('website', 'static', 'images', session.get('image_filename'))
                        script_path = os.path.join('models', 'baa_predictor.py')
                        output = subprocess.check_output(['python', script_path, image_path])
                        output = output.decode('utf-8').strip().strip("'")
                        session['scan_result'] = f"Bone age in months and years: { output } months, { round(float(output)/12, 2) } years"
                        session['scan_type'] = 'Bone Age'
                        flash('Bone Age scan completed successfully!', 'success')
                        session.pop('image_filename', None)
                        return render_template("home.html", user=current_user, scan_data=scan_data, boneoutput_months=output, boneoutput_years = round(float(output)/12, 2))
                    except subprocess.CalledProcessError as e:
                        flash(f'Error running Bone Age scan: {e}', 'danger')

                elif selected_scan == 'fracture':
                    try:
                        image_path = os.path.join('website', 'static', 'images', session.get('image_filename'))
                        script_path = os.path.join('models', 'fracture_predictor.py')
                        output = subprocess.check_output(['python', script_path, image_path])
                        output = output.decode('utf-8').strip().strip("'")
                        output = ast.literal_eval(output)
                        if output:  # Check if the dictionary is not empty
                            formatted_output = ', '.join([f"{key} - {value:.1f}% confidence" for key, value in dict(output).items()])
                            output = f"{formatted_output}"
                        else:
                            output = "Nothing detected - please review."
                        session['scan_result'] = output
                        session['scan_type'] = 'Fracture Detection'
                        flash('Fracture Prediction scan completed successfully!', 'success')
                        session.pop('image_filename', None)
                        return render_template("home.html", user=current_user, scan_data=scan_data, fractureoutput_text=output)
                    except subprocess.CalledProcessError as e:
                        flash(f'Error running Fracture Prediction scan: {e}', 'danger')

                elif selected_scan == 'pneumonia':
                    try:
                        image_path = os.path.join('website', 'static', 'images', session.get('image_filename'))
                        script_path = os.path.join('models', 'pneumonia_detector.py')
                        output = subprocess.check_output(['python', script_path, image_path])
                        output = output.decode('utf-8').strip()
                        if output == 'Pneumonia':
                            session['scan_result'] = "Pneumonia scan result: Positive"
                        else:
                            session['scan_result'] = "Pneumonia scan result: Negative"
                        session['scan_type'] = 'Pneumonia Detection'
                        flash('Pneumonia Prediction scan completed successfully!', 'success')
                        session.pop('image_filename', None)
                        return render_template("home.html", user=current_user, scan_data=scan_data, pneumoniaoutputtext=output)
                    except subprocess.CalledProcessError as e:
                        flash(f'Error running Pneumonia Prediction scan: {e}', 'danger')

                elif selected_scan == 'cancer':
                    try:
                        image_path = os.path.join('website', 'static', 'images', session.get('image_filename'))
                        script_path1 = os.path.join('models', 'cancer_detector.py')
                        script_path2 = os.path.join('models', 'precancer.py')
                        subprocess.run(['python', script_path2])
                        output = subprocess.check_output(['python', script_path1, image_path])
                        output = output.decode('utf-8').strip()
                        cancer_type, confidence_str = output.split()
                        confidence_level = float(confidence_str)
                        # Check the confidence level and reassign the output string
                        if confidence_level < 70.0:
                            output = f"{cancer_type} - low confidence ({confidence_level}%), please review.)"
                        else:
                            output = f"{cancer_type} - {confidence_level}% confidence"
                        session['scan_result'] = output
                        session['scan_type'] = 'Cancer Detection'
                        flash('Cancer Prediction scan completed successfully!', 'success')
                        session.pop('image_filename', None)
                        return render_template("home.html", user=current_user, scan_data=scan_data, canceroutputtext=output)
                    except subprocess.CalledProcessError as e:
                        flash(f'Error running Cancer Prediction scan: {e}', 'danger')

                else:
                    flash('No options selected.', 'danger')
                
            else:
                flash('No image uploaded to scan.', 'danger')

        elif form_name == 'emailForm': 
            #temporary content 
            email_content = request.form.get('note')
            user = User.query.filter_by(email=email_content).first()

            if 'scan_result' not in session or 'scan_type' not in session:
                flash('No scan results available to send.', 'danger')
                return render_template("home.html", user=current_user)
            if user:
                doctoruser_id = current_user.id
                patientuser_id = user.id
                scan_name = session.get('scan_type')
                scan_output = session.get('scan_result')
                scan_datetime = datetime.now()

                # Create new scan record and insert it into the database
                new_scan_record = Scan(
                    doctoruser_id=doctoruser_id,
                    patientuser_id=patientuser_id,
                    date_of_scan=scan_datetime,
                    scan_name=scan_name,
                    scan_result=scan_output
                )
                db.session.add(new_scan_record)
                db.session.commit()
                email = os.getenv('EMAIL_ACCOUNT')
                receiver_email = user.email
                msg = MIMEMultipart()
                msg['From'] = email
                msg['To'] = receiver_email
                msg['Subject'] = f"Scan Results from Dr. {current_user.first_name}: {session['scan_type']}"
                body = f"Here are the results of the latest scan from Dr. {current_user.first_name}:\n\n{session['scan_result']}"
                msg.attach(MIMEText(body, 'plain'))
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(email, os.getenv('GMAIL_APP_PASSWORD'))
                server.send_message(msg)
                flash(f'Scan results sent to {receiver_email}.', 'success')
                return render_template("home.html", user=current_user, user_details=user, scan_data=scan_data)
            else:
                flash('No user with that email exists.', category='error')
    return render_template("home.html", user=current_user, scan_data=scan_data)

@views.route('/contact-us')
def contact_us():
    return render_template('contact_us.html', user=current_user, all_users=User.query.all())