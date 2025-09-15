from flask import Flask
from werkzeug.security import generate_password_hash
from flask_cors import CORS


from application.config import LocalDevelopmentConfig
from application.database import db
from application.models import User
from application.security import jwt
from application.celery_init_app import celery_init_app
from celery.schedules import crontab



app = None

def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"], supports_credentials=True)
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)
    jwt.init_app(app)
    app.app_context().push()

    with app.app_context():
        try:
            db.create_all()
            create_admin()
        except Exception as e:
            print(f"Database initialization error: {e}")
    return app


def create_admin():
    username = "admin"
    existing_user = User.query.filter_by(username = username).first()
    if not existing_user:
        user = User(
            username = "admin",
            email = "admin@gmail.com",
            password_hash = generate_password_hash("admin"),
            full_name = "Admin",
            address = "Rajathan",
            pincode = "306401",
            role = "admin"

        )
        db.session.add(user)
        db.session.commit()
        print("Admin created Successfully")
    else:
        print("Admin already exists")
    print("username: admin")
    print("password: admin")


app = create_app()
celery = celery_init_app(app)
celery.autodiscover_tasks()

@celery.on_after_finalize.connect 
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute = '*/2'),
        monthly_report.s(),
    )

from application.routes import *


if __name__ == "__main__":
    app.run()
