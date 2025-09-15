from datetime import datetime
from .database import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(150), unique = True, nullable = False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable = False)
    full_name = db.Column(db.String(200), nullable = False)
    address = db.Column(db.String(200), nullable = False)
    pincode = db.Column(db.Integer, nullable = False)
    role = db.Column(db.Text, nullable = False, default = "user")
    is_blocked = db.Column(db.Boolean, nullable = False, default = False)

class ParkingLot(db.Model):
    __tablename__ = 'parkinglot'
    id = db.Column(db.Integer, primary_key = True)
    prime_location = db.Column(db.Text, nullable = False)
    price = db.Column(db.Float, nullable = False)
    address = db.Column(db.Text, nullable = False)
    pincode = db.Column(db.Integer, nullable = False)
    number_of_spots = db.Column(db.Integer, nullable = False)
    

class ParkingSpot(db.Model):
    __tablename__ = 'parkingspot'
    id = db.Column(db.Integer, primary_key = True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parkinglot.id'), nullable = False)
    status = db.Column(db.String(1), nullable = False, default = "A") # O- Occupied, A- Available

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parkingspot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_number = db.Column(db.String(50), nullable=False)
    booking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default="active")

class ReserveParkingSpot(db.Model):
    __tablename__ = 'reserveparkingspot'
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parkingspot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    parking_cost = db.Column(db.Float, nullable=False, default=0.0)




