class config():
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalDevelopmentConfig(config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///vehicleDB.sqlite3"
    JWT_SECRET_KEY = "This-is-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = False  # Add this to prevent token expiration issues
    JWT_TOKEN_LOCATION = ["headers"]  # Ensure token is expected in headers
    