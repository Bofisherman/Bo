import os
from flask import Flask
from flask_mail import Mail
from fishcore.config import Config

mail = Mail()

def create_app():
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(__file__), 'static'),
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

    app.config.from_object(Config)
    mail.init_app(app)

    # ✅ Google OAuth blueprint must go here
    from flask_dance.contrib.google import make_google_blueprint
    google_bp = make_google_blueprint(
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scope=["profile", "email"],
        redirect_to="main.google_login"
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    # Register your routes
    from fishcore.routes import main_routes
    app.register_blueprint(main_routes)

    return app
