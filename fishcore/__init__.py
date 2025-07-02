import os
from flask import Flask
from flask_mail import Mail
from fishcore.config import Config,ProductionConfig
from dotenv import load_dotenv
load_dotenv()
from werkzeug.middleware.proxy_fix import ProxyFix



mail = Mail()

def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
        template_folder=os.path.join(os.path.dirname(__file__), 'templates')
    )

    # ✅ Choose config based on environment
    if os.getenv("FLASK_ENV") == "production":
        print("[INFO] Using ProductionConfig")
        app.config.from_object(ProductionConfig)
    else:
        print("[INFO] Using default Config")
        app.config.from_object(Config)

    # 🔎 Print after config is loaded to confirm what Flask sees
    print(f"[DEBUG] SERVER_NAME loaded: {app.config.get('SERVER_NAME')}")

    mail.init_app(app)

    # ✅ Apply ProxyFix to respect proxy headers (important for SERVER_NAME + HTTPS redirects)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # ✅ Google OAuth blueprint must go here
    from flask_dance.contrib.google import make_google_blueprint
    google_bp = make_google_blueprint(
        client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        scope=["profile", "email"],
        redirect_url="https://bofisherman.com/login/google/authorized"
    )

    app.register_blueprint(google_bp, url_prefix="/login")

    # ✅ Register your routes
    from fishcore.routes import main_routes
    app.register_blueprint(main_routes)

    return app
