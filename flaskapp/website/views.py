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
                    return render_template("home.html", user=current_user, image_filename=image_filename)
        elif form_name == 'getChoice': 
            selected_scan = request.form.get('getChoice')
            if selected_scan == 'boneAge':
                if session.get('image_filename'):
                    # Run the baa_predictor.py script with the image path
                    try:
                        image_path = os.path.join('website', 'static', 'images', session.get('image_filename'))
                        script_path = os.path.join('models', 'baa_predictor.py')
                        output = subprocess.check_output(['python', script_path, image_path])
                        output = output.decode('utf-8').strip().strip("'")
                        session['scan_result'] = f"The model predicts a bone age of {output} months ({round(float(output)/12, 2)} years)"
                        session['scan_type'] = 'Bone Age'
                        flash('Bone Age scan completed successfully!', 'success')
                        session.pop('image_filename', None)
                        return render_template("home.html", user=current_user, boneoutput_months=output, boneoutput_years = round(float(output)/12, 2))
                    except subprocess.CalledProcessError as e:
                        flash(f'Error running Bone Age scan: {e}', 'danger')
                else:
                    flash('No image uploaded for Bone Age scan.', 'danger')
            elif selected_scan == 'fracture':
                # Handle Fracture Detection scan logic here
                if session.get('image_filename'):
                    # Run the fracture_predictor.py script with the image path
                    try:
                        image_path = os.path.join('website', 'static', 'images', session.get('image_filename'))
                        script_path = os.path.join('models', 'fracture_predictor.py')
                        output = subprocess.check_output(['python', script_path, image_path])
                        output = output.decode('utf-8').strip().strip("'")
                        output = ast.literal_eval(output)
                        if output:  # Check if the dictionary is not empty
                            formatted_output = ', '.join([f"the model is {value:.1f}% confident of a {key}" for key, value in dict(output).items()])
                            output = f"Results: {formatted_output}"
                        else:
                            output = "Nothing detected - please check for further review."
                        session['scan_result'] = output
                        session['scan_type'] = 'Fracture Detection'
                        flash('Fracture Prediction scan completed successfully!', 'success')
                        session.pop('image_filename', None)
                        return render_template("home.html", user=current_user, fractureoutput_text=output)
                    except subprocess.CalledProcessError as e:
                        flash(f'Error running Fracture Prediction scan: {e}', 'danger')
                else:
                    flash('No image uploaded for Fracture Prediction scan.', 'danger')
            elif selected_scan == 'pneumonia':
                # Handle Pneumonia Detection scan logic here
                if session.get('image_filename'):
                    # Running the pneumonia_detector.py script with the image path
                    try:
                        image_path = os.path.join('website', 'static', 'images', session.get('image_filename'))
                        script_path = os.path.join('models', 'pneumonia_detector.py')
                        output = subprocess.check_output(['python', script_path, image_path])
                        output = output.decode('utf-8').strip()
                        # output = output.decode('utf-8').strip().strip("'")
                        session['scan_result'] = f"Pneumonia scan result: {output}"
                        session['scan_type'] = 'Pneumonia Detection'
                        flash('Pneumonia Prediction scan completed successfully!', 'success')
                        session.pop('image_filename', None)
                        return render_template("home.html", user=current_user, pneumoniaoutputtext=output)
                    except subprocess.CalledProcessError as e:
                        flash(f'Error running Pneumonia Prediction scan: {e}', 'danger')
                else:
                    flash('No image uploaded for Pneumonia Prediction scan.', 'danger')
            elif selected_scan == 'cancer':
                # Handle Cancer Detection scan logic here
                if session.get('image_filename'):
                    # Running the cancer_detector.py script with the image path
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
                            output = f"{cancer_type} (low confidence: please review.)"
                        else:
                            output = f"{cancer_type} {confidence_level}"
                        session['scan_result'] = f"Cancer scan result: {output}"
                        session['scan_type'] = 'Cancer Detection'
                        flash('Cancer Prediction scan completed successfully!', 'success')
                        session.pop('image_filename', None)
                        return render_template("home.html", user=current_user, canceroutputtext=output)
                    except subprocess.CalledProcessError as e:
                        flash(f'Error running Cancer Prediction scan: {e}', 'danger')
                else:
                    flash('No image uploaded for Cancer Prediction scan.', 'danger')
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
                email = "testingthisreallyniceemail@gmail.com"
                receiver_email = user.email
                msg = MIMEMultipart()
                msg['From'] = email
                msg['To'] = receiver_email
                msg['Subject'] = f"Scan Results from Dr. {current_user.first_name}: {session['scan_type']}"
                body = f"Here are the results of the latest scan from Dr. {current_user.first_name}:\n\n{session['scan_result']}"
                msg.attach(MIMEText(body, 'plain'))
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(email, "kwzzvgstqnpcghsy")
                server.send_message(msg)
                flash(f'Scan results sent to {receiver_email}.', 'success')
                return render_template("home.html", user=current_user, user_details=user)
            else:
                flash('No user with that email exists.', category='error')
    return render_template("home.html", user=current_user, scan_data=scan_data)

@views.route('/contact-us')
def contact_us():
    return render_template('contact_us.html', user=current_user, all_users=User.query.all())

