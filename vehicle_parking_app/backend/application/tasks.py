from celery import shared_task
import requests
import datetime
import csv
from jinja2 import Template
from .mail import send_email
from .models import User,ReserveParkingSpot

# Task - 1 Daily Reminders
@shared_task(ignore_results = False, name = "generate_msg")
def generate_msg(username):
    text = f"Hi {username}, your quick park has been generated. Please check the app at http://127.0.0.1:5173"
    response = requests.post("https://chat.googleapis.com/v1/spaces/AAQARFU8F9s/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=3Cvx74gYrQCWECl5qJgVyRBrkZNBTaH5BCwnyazQG8w", json = {"text": text})
    print(response.status_code)
    return "The delivery is sent to user"

# Task - 2 Monthly Report sent via mail
# scheduled job via crontab
@shared_task(ignore_results = False, name = "monthly_report")
def monthly_report():
    users = User.query.filter_by(role = "user").all()
    for user in users:
        user_data = {}
        user_data['username'] = user.username
        user_data['email'] = user.email
        details = []
        parking_details = ReserveParkingSpot.query.filter_by(user_id = user.id).all()
        for info in parking_details:
            info_dict = {}
            info_dict["spot_id"] = info.spot_id
            info_dict["parking_timestamp"] = info.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            info_dict["leaving_timestamp"] = info.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            info_dict["parking_cost"] = info.parking_cost

            details.append(info_dict)
        user_data['details'] = details 
        # till this point you get user data in list of dict form
        mail_template = """
        <h3>Dear {{user_data.username}}</h3>
        <p>Please find the current status of your parking details in the table below.</p>
        <p>Visit our quick park app at http://127.0.0.1:5173 for details.</p>
        <table>
            <tr>
                <th>Spot Id</th>
                <th>Parking Timestamp</th>
                <th>Leaving Timestamp</th>
                <th>Parking Cost</th>
            </th>
            </tr>
            {% for detail in user_data.details %}
            <tr>
                <td>{{ detail.spot_id }}</td>
                <td>{{ detail.parking_timestamp }}</td>
                <td>{{ detail.leaving_timestamp }}</td>
                <td>{{ detail.parking_cost }}</td>
               

            </tr>
            {% endfor %}
        </table>
        <h5>Regards<br>
        <h5>Quick Park<br>
        <h5>Department of Data Science, IIT Madras</h5>
        """
        message = Template(mail_template).render(user_data = user_data)
        # the data is then rendered into a mail body
        if user.email:
            send_email(user.email, subject = "Monthly card detail Report - Quick Park", message = message)
        else:
            print(f"[ERROR] Skipping email for user: {user.username} - Invalid email: {user.email}")

    return "Monthly reports sent" 

# user_data = {
#     username: 
#     email:
#     details: [
#         {
#             spot_id:
#             parking_timestamp:
#             leaving_timestamp:
#             parking_cost:
#         }
#     ]
# }




# Task -3 Download CSV report for user
#Usr(client) triggered async job
@shared_task(ignore_results = False, name = "csv_report")
def csv_report(user_id):
    parking_details = ReserveParkingSpot.query.filter_by(user_id=user_id).all()
    if not parking_details:
        return f"No parking history found for user ID: {user_id}"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file_name = f"Parking_details_{user_id}_{timestamp}.csv"
    file_path = f'static/{csv_file_name}'
    with open(file_path, 'w', newline="") as csvfile:
        parking_csv = csv.writer(csvfile, delimiter=',')
        parking_csv.writerow(['Sr No.', 'Spot Id', 'User ID', 'Parking Timestamp', 'Leaving Timestamp', 'Parking Cost'])
        for i, detail in enumerate(parking_details, 1):
            this_parking = [i, detail.spot_id, detail.user_id, detail.parking_timestamp, detail.leaving_timestamp, detail.parking_cost]
            parking_csv.writerow(this_parking)
    return csv_file_name








