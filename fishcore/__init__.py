import os
from flask import Flask
from flask_mail import Mail
from .config import Config

mail = Mail()

def create_app():
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(__file__), 'static'),
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'))

    # Load app config
    app.config.from_object(Config)

    # Initialize Flask-Mail
    mail.init_app(app)

    # Register routes blueprint
    from .routes import main_routes
    app.register_blueprint(main_routes)

    # Ensure folders exist
    os.makedirs(os.path.join(app.static_folder, 'videos'), exist_ok=True)
    os.makedirs(os.path.join(app.static_folder, 'images'), exist_ok=True)

    return app
