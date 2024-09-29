from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    isdoctor = db.Column(db.String(150))
    notes = db.relationship('Note')

class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctoruser_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    patientuser_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_of_scan = db.Column(db.DateTime(timezone=True), default=func.now())
    scan_name = db.Column(db.String(150))
    scan_result = db.Column(db.String(10000))
    doctor = db.relationship('User', foreign_keys=[doctoruser_id])
    patient = db.relationship('User', foreign_keys=[patientuser_id])