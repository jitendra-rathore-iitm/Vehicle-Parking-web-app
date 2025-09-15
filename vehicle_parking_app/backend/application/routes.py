from flask import current_app as app, jsonify, request, abort
from flask import send_from_directory
from flask_jwt_extended import current_user, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import math
from sqlalchemy import func
from .database import db
from .models import User, ParkingLot, ParkingSpot, ReserveParkingSpot, Booking
from celery.result import AsyncResult
from .tasks import csv_report, monthly_report, generate_msg






def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify(message = "Admin access required"), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods = ["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    address = data.get("address")
    pincode = data.get("pincode")
    if not all([username, password, full_name, address, pincode, email]):
        return jsonify(message = "All fields are required"), 400
    if User.query.filter_by(username = username).first():
        return jsonify(message = "Username is already exists!"), 400
    if User.query.filter_by(email = email).first():
        return jsonify(message = "Email is already exists!"), 400
    user = User(username = username, password_hash = generate_password_hash(password), full_name = full_name, address = address, pincode = pincode, email = email)
    db.session.add(user)
    db.session.commit()
    return jsonify(message = "User registered successfully"), 200

@app.route("/login", methods = ['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username = username).first()
    if user and user.is_blocked:
        return jsonify({'message': 'Your account has been blocked'}), 403
    
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(identity = str(user.id))
        return jsonify(message = "Login Successful", access_token = access_token, role = user.role), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401




@app.route("/admin/add/parkinglot", methods = ['POST'])
@admin_required
def create_parking_lot():
    data = request.json

    try:
        prime_location = data.get("prime_location")
        price = data.get("price")
        address = data.get("address")
        pincode = data.get("pincode")
        number_of_spots = int(data.get("number_of_spots", 0))
    except (ValueError, TypeError):
        return jsonify(message = "Invalid Data type"), 422
    
    if not all([prime_location, price, address, pincode, number_of_spots]):
        return jsonify(message = "All fields are required"), 400
    
    parking_lot = ParkingLot(prime_location = prime_location, price = price, address = address, pincode = pincode, number_of_spots = number_of_spots)
    db.session.add(parking_lot)
    db.session.commit()

    for i in range(number_of_spots):
        parking_spot = ParkingSpot(lot_id = parking_lot.id, status = 'A')
        db.session.add(parking_spot)
    db.session.commit()
    return jsonify(message = "Parking Lot created successfully"), 200

@app.route("/admin/parkinglot/<int:lot_id>", methods = ['GET'])
@admin_required
def get_parking_lot(lot_id):
    parking_lot = ParkingLot.query.get(lot_id)
    if not parking_lot:
        return jsonify(message = "Parking Lot not found"), 404
    
    # Get spot information
    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    occupied_spots = [spot for spot in spots if spot.status == "O"]
    available_spots = [spot for spot in spots if spot.status == "A"]
    
    return jsonify({
        "id": parking_lot.id,
        "prime_location": parking_lot.prime_location,
        "address": parking_lot.address,
        "price": parking_lot.price,
        "pincode": parking_lot.pincode,
        "number_of_spots": parking_lot.number_of_spots,
        "occupied_spots": len(occupied_spots),
        "available_spots": len(available_spots)
    }), 200



@app.route("/admin/edit/parkingLot/<int:lot_id>", methods = ['PUT'])
@admin_required
def edit_parking_lot(lot_id):
    parking_lot = ParkingLot.query.get(lot_id)

    if not parking_lot:
        return jsonify(message = "Parking Lot not found"), 404
    
    data = request.json
    if not data:
        return jsonify(message = "No data is provided"), 400
    
    # Get current spots and occupied count
    current_spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
    occupied_spots = [spot for spot in current_spots if spot.status == "O"]
    occupied_count = len(occupied_spots)
    
    # Check if reducing spots and there are occupied spots
    new_spots_count = data.get("number_of_spots", parking_lot.number_of_spots)
    if new_spots_count < len(current_spots) and occupied_count > 0:
        return jsonify(
            message = f"Cannot reduce spots. {occupied_count} spots are currently occupied by users.",
            occupied_count = occupied_count,
            current_spots = len(current_spots),
            requested_spots = new_spots_count
        ), 400
    
    # Update basic info
    parking_lot.prime_location = data.get("prime_location", parking_lot.prime_location)
    parking_lot.price = data.get("price", parking_lot.price)
    parking_lot.address = data.get("address", parking_lot.address)
    parking_lot.pincode = data.get("pincode", parking_lot.pincode)
    
    # Handle spot management
    current_spots_count = len(current_spots)
    if new_spots_count != current_spots_count:
        if new_spots_count > current_spots_count:
            # Adding more spots
            for i in range(new_spots_count - current_spots_count):
                new_spot = ParkingSpot(lot_id=lot_id, status='A')
                db.session.add(new_spot)
        else:
            # Reducing spots (only if no occupied spots)
            spots_to_remove = current_spots[new_spots_count:]
            for spot in spots_to_remove:
                db.session.delete(spot)
    
    parking_lot.number_of_spots = new_spots_count
    db.session.commit()
    
    return jsonify(message = "Parking lot updated successfully"), 200

@app.route("/admin/delete/parkingLot/<int:lot_id>", methods = ["DELETE"])
@admin_required
def delete_parking_lot(lot_id):
    parking_lot = ParkingLot.query.get(lot_id)
    if not parking_lot:
        return jsonify(message = "Parking Lot not found"), 404
    spots = ParkingSpot.query.filter_by(lot_id = lot_id).all()
    if any(spot.status == "O" for spot in spots):
        return jsonify(message = "Some spots are occupied by other users"), 400
    for spot in spots:
        db.session.delete(spot)
    db.session.delete(parking_lot)
    db.session.commit()
    return jsonify(message = "Parking Lot deleted successfully"), 200

@app.route("/admin/parkinglots/show", methods = ["GET"])
@admin_required
def get_all_parking_lots():
    parking_lots = ParkingLot.query.all()
    result = []
    
    for lot in parking_lots:
        # Get all spots for this parking lot
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()
        spots_data = [{
            "id": spot.id,
            "status": spot.status
        } for spot in spots]
        
        lot_data = {
            "id": lot.id,
            "prime_location": lot.prime_location,
            "address": lot.address,
            "price": lot.price,
            "pincode": lot.pincode,
            "number_of_spots": lot.number_of_spots,
            "available_spots": ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count(),
            "spots": spots_data
        }
        result.append(lot_data)
    
    return jsonify(parking_lots = result), 200

@app.route("/user/parkinglots/next-available-spot/<int:lot_id>", methods = ['GET'])
@jwt_required()
def get_next_available_spot(lot_id):
    """Get the next available spot ID for a parking lot"""
    try:
        # Verify parking lot exists
        parking_lot = ParkingLot.query.get(lot_id)
        if not parking_lot:
            return jsonify(message="Parking lot not found"), 404
        
        # Find the first available spot
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').order_by(ParkingSpot.id).first()
        
        if not available_spot:
            return jsonify(message="No available spots in this parking lot"), 404
        
        return jsonify({
            "lot_id": lot_id,
            "next_available_spot_id": available_spot.id,
            "total_spots": parking_lot.number_of_spots,
            "available_spots": ParkingSpot.query.filter_by(lot_id=lot_id, status='A').count()
        }), 200
        
    except Exception as e:
        print(f"Error getting next available spot: {str(e)}")
        return jsonify(message=f"Error getting next available spot: {str(e)}"), 500

@app.route("/admin/users/show", methods = ["GET"])
@admin_required
def view_users():
    users = User.query.filter_by(role = "user").all()
    if not users:
        return jsonify(message = "No users found"), 404
    user_list = [{
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "pincode": user.pincode,
        "address": user.address,
        "is_blocked": user.is_blocked
    } for user in users]
    return jsonify(users = user_list), 200



@app.route("/admin/block/user/<int:user_id>", methods=["POST"])
@admin_required
def block_user(user_id):
    user = User.query.get(user_id)
    if not user or user.role != "user":
        return jsonify(message="User not found"), 404
    user.is_blocked = True
    db.session.commit()
    return jsonify(message="User blocked successfully"), 200

@app.route("/admin/unblock/user/<int:user_id>", methods=["POST"])
@admin_required
def unblock_user(user_id):
    user = User.query.get(user_id)
    if not user or user.role != "user":
        return jsonify(message="User not found"), 404
    user.is_blocked = False
    db.session.commit()
    return jsonify(message="User unblocked successfully"), 200

@app.route('/admin/profile', methods=['GET'])
@admin_required
def get_admin_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify(message='Admin not found'), 404
    return jsonify({
        'username': user.username,
        'email': user.email, 
        'full_name': user.full_name,
        'address': user.address,
        'pincode': user.pincode
    }), 200

@app.route('/admin/profile', methods=['PUT'])
@admin_required
def update_admin_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'admin':
        return jsonify(message='Admin not found'), 404
    data = request.json
    if 'username' in data:
        if User.query.filter(User.username == data['username'], User.id != user_id).first():
            return jsonify(message='Username already exists'), 400
        user.username = data['username']
    if 'email' in data:
        if User.query.filter(User.email == data['email'], User.id != user_id).first():
            return jsonify(message='Email already exists'), 400
        user.email = data['email']
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'address' in data:
        user.address = data['address']
    if 'pincode' in data:
        user.pincode = data['pincode']
    if 'password' in data and data['password']:
        user.password_hash = generate_password_hash(data['password'])
    db.session.commit()
    return jsonify(message='Profile updated successfully'), 200

@app.route("/admin/spot-details/<int:lot_id>/<int:spot_id>", methods = ['GET'])
@admin_required
def get_spot_details(lot_id, spot_id):
    # Get the parking lot
    parking_lot = ParkingLot.query.get(lot_id)
    if not parking_lot:
        return jsonify(message = "Parking Lot not found"), 404
    
    # Get the specific spot by ID
    spot = ParkingSpot.query.filter_by(id=spot_id, lot_id=lot_id).first()
    if not spot:
        return jsonify(message = "Spot not found"), 404
    
    # Basic spot info
    spot_info = {
        "spot_id": spot.id,
        "status": spot.status,
        "lot_id": lot_id
    }
    
    # If spot is occupied, get booking details
    if spot.status == "O":
        # First try to get booking from Booking table (regular bookings)
        booking = Booking.query.filter_by(spot_id=spot.id).order_by(Booking.booking_timestamp.desc()).first()
        
        if booking:
            # Get user details
            user = User.query.get(booking.user_id)
            
            spot_info["booking"] = {
                "user_id": booking.user_id,
                "customer_name": user.full_name if user else "Unknown",
                "vehicle_number": booking.vehicle_number,
                "parking_timestamp": booking.booking_timestamp.isoformat() if booking.booking_timestamp else None,
                "parking_cost": 0,  # Regular bookings don't have cost yet
                "booking_type": "Regular Booking"
            }
        else:
            # Try to get from ReserveParkingSpot table (reservations/park-ins)
            reserve_booking = ReserveParkingSpot.query.filter_by(spot_id=spot.id).order_by(ReserveParkingSpot.parking_timestamp.desc()).first()
            
            if reserve_booking:
                # Get user details
                user = User.query.get(reserve_booking.user_id)
                
                spot_info["booking"] = {
                    "user_id": reserve_booking.user_id,
                    "customer_name": user.full_name if user else "Unknown",
                    "vehicle_number": "N/A",  # Vehicle number not stored in ReserveParkingSpot
                    "parking_timestamp": reserve_booking.parking_timestamp.isoformat() if reserve_booking.parking_timestamp else None,
                    "parking_cost": reserve_booking.parking_cost if reserve_booking.parking_cost else 0,
                    "booking_type": "Reservation/Park-in"
                }
            else:
                # Spot is marked as occupied but no booking found
                spot_info["booking"] = {
                    "user_id": "Unknown",
                    "customer_name": "Unknown",
                    "vehicle_number": "N/A",
                    "parking_timestamp": None,
                    "parking_cost": 0,
                    "booking_type": "No booking record found"
                }
    
    return jsonify(spot_info), 200

@app.route("/user/parkinglots/show", methods = ['GET'])
@jwt_required()
def user_get_parking_lots():
    parking_lots = ParkingLot.query.all()
    result = [{
        "id": lot.id,
        "prime_location": lot.prime_location,
        "address": lot.address,
        "price": lot.price,
        "pincode": lot.pincode,
        "number_of_spots": lot.number_of_spots,
        "available_spots": ParkingSpot.query.filter_by(lot_id=lot.id, status='A').count()
    } for lot in parking_lots]
    return jsonify(parking_lots = result), 200

@app.route("/user/parkinglots/book", methods=['POST'])
@jwt_required()
def user_book_parking_spot():
    try:
        data = request.get_json()
        lot_id = data.get('lot_id')
        vehicle_number = data.get('vehicle_number')

        if not lot_id or not vehicle_number:
            return jsonify(message="Lot ID and vehicle number are required"), 400

        try:
            lot_id = int(lot_id)
        except (ValueError, TypeError):
            return jsonify(message="Invalid lot ID format"), 400

        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify(message="Invalid user ID"), 400

        user = User.query.get(current_user_id)
        if not user:
            return jsonify(message="User not found"), 404
        if user.is_blocked:
            return jsonify(message="Your account has been blocked"), 403

        parking_lot = ParkingLot.query.get(lot_id)
        if not parking_lot:
            return jsonify(message="Parking lot not found"), 404

        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').order_by(ParkingSpot.id).first()
        if not available_spot:
            return jsonify(message="No available spots in this parking lot"), 400

        ist_offset = timedelta(hours=5, minutes=30)
        current_time = datetime.utcnow() + ist_offset

        # Create Booking
        booking = Booking(
            spot_id=available_spot.id,
            user_id=current_user_id,
            vehicle_number=vehicle_number,
            booking_timestamp=current_time,
            status="booked"
        )
        db.session.add(booking)

        # Create Reservation
        reservation = ReserveParkingSpot(
            spot_id=available_spot.id,
            user_id=current_user_id,
            parking_timestamp=current_time,
            leaving_timestamp=current_time,  # Will update on release
            parking_cost=0.0
        )
        db.session.add(reservation)

        # Mark spot as occupied
        available_spot.status = 'O'

        # Commit all changes at once
        db.session.commit()

        return jsonify({
            "message": "Parking spot booked successfully",
            "booking_id": booking.id,
            "reservation_id": reservation.id,
            "spot_id": available_spot.id,
            "lot_id": lot_id
        }), 200

    except Exception as e:
        print(f"Error in booking: {str(e)}")
        db.session.rollback()
        return jsonify(message=f"Error booking parking spot: {str(e)}"), 500


@app.route("/user/parkinglots/reserve", methods = ['POST'])
@jwt_required()
def user_reserve_parking_spot():
    try:
        data = request.get_json()
        print(f"Received reservation data: {data}")  # Debug print
        
        lot_id = data.get('lot_id')
        vehicle_number = data.get('vehicle_number')
        
        print(f"Lot ID: {lot_id}, Vehicle Number: {vehicle_number}")  # Debug print
        
        if not lot_id or not vehicle_number:
            return jsonify(message="Lot ID and vehicle number are required"), 400
        
        # Convert lot_id to integer
        try:
            lot_id = int(lot_id)
        except (ValueError, TypeError):
            return jsonify(message="Invalid lot ID format"), 400
        
        # Get current user ID from JWT and convert to integer
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify(message="Invalid user ID"), 400
        
        print(f"Current user ID: {current_user_id}")  # Debug print
        
        # Verify user exists and is not blocked
        user = User.query.get(current_user_id)
        if not user:
            return jsonify(message="User not found"), 404
        if user.is_blocked:
            return jsonify(message="Your account has been blocked"), 403
        
        # Verify parking lot exists
        parking_lot = ParkingLot.query.get(lot_id)
        if not parking_lot:
            return jsonify(message="Parking lot not found"), 404
        
        # Find the first available spot in the parking lot (automatic allocation)
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').order_by(ParkingSpot.id).first()
        print(f"First available spot found: {available_spot}")  # Debug print
        
        if not available_spot:
            return jsonify(message="No available spots in this parking lot"), 400
        
        # Create booking with active status
        ist_offset = timedelta(hours=5, minutes=30)
        current_time = datetime.utcnow() + ist_offset
        booking = Booking(
            spot_id=available_spot.id,
            user_id=current_user_id,
            vehicle_number=vehicle_number,
            booking_timestamp=current_time,
            status="active"  # Status: active (reserved)
        )
        db.session.add(booking)
        print(f"Booking created: {booking.id}")  # Debug print
        
        # Create reservation (this marks the spot as occupied)
        reservation = ReserveParkingSpot(
            spot_id=available_spot.id,
            user_id=current_user_id,
            parking_timestamp=current_time,
            leaving_timestamp=current_time,  # Will be updated when leaving
            parking_cost=0.0  # Will be calculated when leaving
        )
        db.session.add(reservation)
        print(f"Reservation created")  # Debug print
        
        # Mark spot as occupied
        available_spot.status = 'O'
        print(f"Spot status updated to occupied")  # Debug print
        
        db.session.commit()
        print(f"Database committed successfully")  # Debug print
        
        return jsonify({
            "message": "Parking spot reserved successfully",
            "booking_id": booking.id,
            "reservation_id": reservation.id,
            "spot_id": available_spot.id,
            "lot_id": lot_id
        }), 200
        
    except Exception as e:
        print(f"Error in reservation: {str(e)}")  # Debug print
        db.session.rollback()
        return jsonify(message=f"Error reserving parking spot: {str(e)}"), 500

@app.route("/user/parkinglots/park-in", methods = ['POST'])
@jwt_required()
def user_park_in():
    try:
        data = request.get_json()
        lot_id = data.get('lot_id')
        vehicle_number = data.get('vehicle_number')
        
        if not lot_id or not vehicle_number:
            return jsonify(message="Lot ID and vehicle number are required"), 400
        
        # Convert lot_id to integer
        try:
            lot_id = int(lot_id)
        except (ValueError, TypeError):
            return jsonify(message="Invalid lot ID format"), 400
        
        # Get current user ID from JWT
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify(message="Invalid user ID"), 400
        
        # Verify user exists and is not blocked
        user = User.query.get(current_user_id)
        if not user:
            return jsonify(message="User not found"), 404
        if user.is_blocked:
            return jsonify(message="Your account has been blocked"), 403
        
        # Verify parking lot exists
        parking_lot = ParkingLot.query.get(lot_id)
        if not parking_lot:
            return jsonify(message="Parking lot not found"), 404
        
        # Find the first available spot in the parking lot (automatic allocation)
        available_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').order_by(ParkingSpot.id).first()
        
        if not available_spot:
            return jsonify(message="No available spots in this parking lot"), 400
        
        # Create booking with active status (vehicle is actually parked)
        ist_offset = timedelta(hours=5, minutes=30)
        current_time = datetime.utcnow() + ist_offset
        booking = Booking(
            spot_id=available_spot.id,
            user_id=current_user_id,
            vehicle_number=vehicle_number,
            booking_timestamp=current_time,
            parking_timestamp=current_time,  # Record actual parking time
            status="active"  # Status: active (vehicle is parked)
        )
        db.session.add(booking)
        
        # Create reservation (this marks the spot as occupied)
        reservation = ReserveParkingSpot(
            spot_id=available_spot.id,
            user_id=current_user_id,
            parking_timestamp=current_time,
            leaving_timestamp=current_time,  # Will be updated when leaving
            parking_cost=0.0  # Will be calculated when leaving
        )
        db.session.add(reservation)
        
        # Mark spot as occupied (vehicle is actually parked)
        available_spot.status = 'O'
        
        db.session.commit()
        
        return jsonify({
            "message": "Vehicle parked successfully",
            "booking_id": booking.id,
            "reservation_id": reservation.id,
            "spot_id": available_spot.id,
            "lot_id": lot_id,
            "parking_time": current_time.isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error parking in: {str(e)}")
        db.session.rollback()
        return jsonify(message=f"Error parking vehicle: {str(e)}"), 500

@app.route("/user/parkinglots/release", methods = ['POST'])
@jwt_required()
def user_release_parking_spot():
    try:
        data = request.get_json()
        spot_id = data.get('spot_id')
        action = data.get('action', 'release')  # 'release' or 'parking_out'
        
        if not spot_id:
            return jsonify(message="Spot ID is required"), 400
        
        # Get current user ID from JWT
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify(message="Invalid user ID"), 400
        
        # Verify user exists and is not blocked
        user = User.query.get(current_user_id)
        if not user:
            return jsonify(message="User not found"), 404
        if user.is_blocked:
            return jsonify(message="Your account has been blocked"), 403
        
        # Find the parking spot
        parking_spot = ParkingSpot.query.get(spot_id)
        if not parking_spot:
            return jsonify(message="Parking spot not found"), 404
        
        # Check if spot is occupied
        if parking_spot.status != 'O':
            return jsonify(message="Spot is not occupied"), 400
        
        # Find the reservation for this spot and user
        reservation = ReserveParkingSpot.query.filter_by(
            spot_id=spot_id, 
            user_id=current_user_id
        ).order_by(ReserveParkingSpot.parking_timestamp.desc()).first()
        
        if not reservation:
            return jsonify(message="No active reservation found for this spot"), 404
        
        # Calculate parking duration and cost
        # Calculate parking duration and cost
        ist_offset = timedelta(hours=5, minutes=30)
        current_time = datetime.utcnow() + ist_offset
        parking_duration_hours = (current_time - reservation.parking_timestamp).total_seconds() / 3600

        # Round up to nearest hour and charge accordingly
        hours_charged = max(1, math.ceil(parking_duration_hours))  # Always round up
        parking_lot = ParkingLot.query.get(parking_spot.lot_id)
        parking_cost = hours_charged * parking_lot.price

        # Update reservation with cost
        reservation.leaving_timestamp = current_time
        reservation.parking_cost = parking_cost

        
        # Update booking with leaving time and status based on action
        booking = Booking.query.filter_by(
            spot_id=spot_id, 
            user_id=current_user_id,
            status="active"
        ).first()
        
        if booking:
            booking.leaving_timestamp = current_time
            if action == 'parking_out':
                booking.status = "parking out"
            else:
                booking.status = "released"
        
        # Mark spot as available
        parking_spot.status = 'A'
        
        db.session.commit()
        
        action_message = "Vehicle marked as parking out" if action == 'parking_out' else "Parking spot released successfully"
        
        return jsonify({
            "message": action_message,
            "parking_duration_hours": round(parking_duration_hours, 2),
            "hours_charged": hours_charged,
            "parking_cost": round(parking_cost, 2),
            "spot_id": spot_id,
            "action": action
        }), 200

        
    except Exception as e:
        print(f"Error releasing parking spot: {str(e)}")
        db.session.rollback()
        return jsonify(message=f"Error releasing parking spot: {str(e)}"), 500

@app.route("/user/parkinglots/history", methods = ['GET'])
@jwt_required()
def user_parking_history():
    try:
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify(message="Invalid user ID"), 400
        
        # Get all bookings for this user, most recent first
        bookings = Booking.query.filter_by(user_id=current_user_id).order_by(Booking.booking_timestamp.desc()).all()
        history_map = {}
        for booking in bookings:
            spot_id = booking.spot_id
            # Find the latest reservation for this spot/user
            reservation = ReserveParkingSpot.query.filter_by(spot_id=spot_id, user_id=current_user_id).order_by(ReserveParkingSpot.parking_timestamp.desc()).first()
            parking_spot = ParkingSpot.query.get(spot_id)
            parking_lot = ParkingLot.query.get(parking_spot.lot_id) if parking_spot else None
            vehicle_number = booking.vehicle_number
            # Default values
            parking_timestamp = booking.booking_timestamp
            leaving_timestamp = None
            parking_cost = 0.0
            hours_charged = 0
            is_active = booking.status == "active"
            booking_status = booking.status
            
            # Check if reservation exists and has been released
            if reservation:
                # If leaving_timestamp is greater than parking_timestamp, it's been released
                if reservation.leaving_timestamp and reservation.leaving_timestamp > reservation.parking_timestamp:
                    leaving_timestamp = reservation.leaving_timestamp
                    # Calculate hours charged
                    duration_hours = (leaving_timestamp - reservation.parking_timestamp).total_seconds() / 3600
                    hours_charged = max(1, math.ceil(duration_hours))
                    parking_cost = reservation.parking_cost
                    is_active = False
                    booking_status = 'parking out'
            
            # Compose history item
            history_item = {
                "spot_id": spot_id,
                "lot_id": parking_spot.lot_id if parking_spot else None,
                "location": parking_lot.prime_location if parking_lot else "Unknown",
                "vehicle_number": vehicle_number,
                "parking_timestamp": parking_timestamp.isoformat() if parking_timestamp else None,
                "leaving_timestamp": leaving_timestamp.isoformat() if leaving_timestamp else None,
                "parking_cost": parking_cost,
                "hours_charged": hours_charged,
                "is_active": is_active,
                "booking_status": booking_status,
                "spot_status": parking_spot.status if parking_spot else None
            }
            # Only keep the latest booking for each spot
            if spot_id not in history_map:
                history_map[spot_id] = history_item
        # Sort by parking_timestamp descending
        history_data = sorted(history_map.values(), key=lambda x: x['parking_timestamp'], reverse=True)
        return jsonify(history=history_data), 200
    except Exception as e:
        print(f"Error fetching parking history: {str(e)}")
        return jsonify(message=f"Error fetching parking history: {str(e)}"), 500

@app.route('/user/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'user':
        return jsonify(message='User not found'), 404
    return jsonify({
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'address': user.address,
        'pincode': user.pincode
    }), 200

@app.route('/user/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or user.role != 'user':
        return jsonify(message='User not found'), 404
    data = request.json
    if 'username' in data:
        if User.query.filter(User.username == data['username'], User.id != user_id).first():
            return jsonify(message='Username already exists'), 400
        user.username = data['username']
    if 'email' in data:
        if User.query.filter(User.email == data['email'], User.id != user_id).first():
            return jsonify(message='Email already exists'), 400
        user.email = data['email']
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'address' in data:
        user.address = data['address']
    if 'pincode' in data:
        user.pincode = data['pincode']
    if 'password' in data and data['password']:
        user.password_hash = generate_password_hash(data['password'])
    db.session.commit()
    return jsonify(message='Profile updated successfully'), 200

@app.route("/admin/summary/revenue", methods=['GET'])
@admin_required
def get_revenue_summary():
    revenue_data = db.session.query(
        ParkingLot.prime_location,
        func.sum(ReserveParkingSpot.parking_cost)
    ).join(ParkingSpot, ParkingLot.id == ParkingSpot.lot_id)\
     .join(ReserveParkingSpot, ParkingSpot.id == ReserveParkingSpot.spot_id)\
     .group_by(ParkingLot.prime_location).all()

    result = [{"location": location, "revenue": revenue} for location, revenue in revenue_data]
    return jsonify(result), 200

@app.route("/admin/summary/slots", methods=['GET'])
@admin_required
def get_slots_summary():
    available_spots = ParkingSpot.query.filter_by(status='A').count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    return jsonify(available_spots=available_spots, occupied_spots=occupied_spots), 200

@app.route("/user/summary/slots", methods=['GET'])
@jwt_required()
def get_user_slots_summary():
    try:
        current_user_id = get_jwt_identity()
        try:
            current_user_id = int(current_user_id)
        except (ValueError, TypeError):
            return jsonify(message="Invalid user ID"), 400

        # Ensure user exists
        user = User.query.get(current_user_id)
        if not user:
            return jsonify(message="User not found"), 404

        usage_data = db.session.query(
            ParkingLot.prime_location,
            func.count(Booking.id)
        ).join(ParkingSpot, ParkingLot.id == ParkingSpot.lot_id)\
         .join(Booking, ParkingSpot.id == Booking.spot_id)\
         .filter(Booking.user_id == current_user_id)\
         .group_by(ParkingLot.prime_location).all()

        result = [{"location": location, "count": count} for location, count in usage_data]
        return jsonify(result), 200
    except Exception as e:
        # Return the actual error message for debugging purposes
        return jsonify(message=f"An unexpected error occurred: {str(e)}"), 500

@app.route('/user/export-csv', methods=['POST'])
@jwt_required()
def trigger_export_csv():
    user_id = get_jwt_identity()
    export_as_csv.delay(user_id)
    return jsonify({"message": "CSV export has been triggered. You will be notified when it's complete."}), 202



# backend Jobs trigger
@app.route('/export_csv', methods=['GET'])
@jwt_required()
def export_csv():
    try:
        user_id = get_jwt_identity()
        task = csv_report.delay(user_id) 
        
        return jsonify({
            "message": "CSV export has been triggered. You will be notified when it's complete.",
            "task_id": task.id
        }), 202
    except Exception as e:
        print(f"Error triggering CSV export: {e}")
        return jsonify(message="Failed to start CSV export"), 500

@app.route('/api/csv_result/<id>') # just create to test the status of result
def csv_result(id):
    res = AsyncResult(id)
    return send_from_directory('static', res.result)

@app.route('/api/send_mail')
def send_mail():
    res = monthly_report.delay()
    return {
        "message": res.result
    }
