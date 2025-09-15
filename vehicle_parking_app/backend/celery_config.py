from celery.schedules import crontab

broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/1"
timezone = 'Asia/Kolkata'
broker_connection_retry_on_startup = True

beat_schedule = {
    'daily-reminders': {
        'task': 'application.tasks.daily_reminders',
        # Runs every day at 7 PM
        'schedule': crontab(hour=19, minute=0),
    },
    'monthly-activity-report': {
        'task': 'application.tasks.monthly_activity_report',
        # Runs on the first day of every month at midnight
        'schedule': crontab(day_of_month=1, hour=0, minute=0),
    },
}


