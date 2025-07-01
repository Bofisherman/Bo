import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

    # SMTP (Brevo) settings
    MAIL_SERVER = 'smtp-relay.brevo.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = "register@bofisherman.com"  # your verified sender

    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = os.environ.get("MAIL_SUPPRESS_SEND", "false").lower() == "true"

    if not MAIL_PASSWORD:
        raise RuntimeError("MAIL_PASSWORD environment variable not set. Aborting startup!")

    # Session & file uploads
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False
    UPLOAD_FOLDER = 'static'
    ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm', 'jpg', 'jpeg', 'png', 'gif'}

class ProductionConfig(Config):
    SERVER_NAME = "bofisherman.com"
    PREFERRED_URL_SCHEME = "https"