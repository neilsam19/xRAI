from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from .models import User
from . import db
import json
import subprocess  # Import subprocess module
import os  # Import os module for path manipulation
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        form_name = request.form.get('form_name')  # Get the form name from the hidden input
        if form_name == 'imageUploadForm':
            if current_user.isdoctor == 'Yes':
                image = request.files['image']
                if image:
                    image_path = f'website/static/images/{image.filename}'
                    image.save(image_path)
                    image_filename = image.filename  # Store the filename
                    subprocess.run(['python', 'website/image_processing.py', image_path])
                    return render_template("home.html", user=current_user, image_filename=image_filename)
        elif form_name == 'emailForm': 
            #temporary content 
            email_content = request.form.get('note')
            user = User.query.filter_by(email=email_content).first()
            if user:
                email = "testingthisreallyniceemail@gmail.com"
                receiver_email = user.email
                msg = MIMEMultipart()
                msg['From'] = email
                msg['To'] = receiver_email
                msg['Subject'] = "Subject Line Here"
                body = "This is the body of the email."
                msg.attach(MIMEText(body, 'plain'))
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(email, "kwzzvgstqnpcghsy")
                server.send_message(msg)
                return render_template("home.html", user=current_user, user_details=user)
            else:
                flash('No user with that email exists.', category='error')
    return render_template("home.html", user=current_user)


