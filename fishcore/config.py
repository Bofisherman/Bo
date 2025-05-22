import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

    MAIL_SERVER = 'smtp-relay.brevo.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = '8d66bd001@smtp-brevo.com'
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = '8d66bd001@smtp-brevo.com'

    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False

    UPLOAD_FOLDER = 'static'
    ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm', 'jpg', 'jpeg', 'png', 'gif'}
