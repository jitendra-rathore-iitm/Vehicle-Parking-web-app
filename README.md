# Vehicle-Parking-web-app
## A. Backend setup

### 1. Create and Activate a Virtual Environment 

```bash
Run the following commands in your backend directory inside the project directory:
# Create a virtual environment
python -m venv venv

# Activate the virtual environment (Windows)
venv\Scripts\activate
```
You should see (venv) in your terminal indicating that the virtual environment is active.

### 2. Run the Application

```bash
python app.py
```
# Frontend
### 1. Ensure the following tools are installed on your machine:

- [Node.js (v16+ recommended)](https://nodejs.org/)
- [npm](https://www.npmjs.com/)

You can verify installations using:

```bash
node -v
npm -v
```

### 2. Install dependencies

Install required packages (inside project folder)

```bash
npm install
```
### 3. Run the development server

```bash
npm run dev
```
### Start Redis Server
Ensure Redis is installed and start the Redis server:
```bash
redis-server
```
To check if Redis is running:
```bash
redis-cli ping  # Should return 'PONG'
```

---
### Start Celery Worker
```bash
cd backend  # Ensure you're in the backend directory
celery -A app.celery worker --loglevel=info
```

---
### Start Celery Beat
```bash
celery -A app.celery beat --loglevel=info
```
### Mail-Hog
```bash
MailHog
```
### **Stopping Services**
To stop the services:
```bash
sudo service redis-server stop  # Stop Redis or
sudo service redis-server start 
pkill -f "celery"  # Stop Celery worker and beat
```
