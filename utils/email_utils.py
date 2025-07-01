from flask_mail import Message
from fishcore import mail
from flask import current_app

def send_email(to, subject, html):
    """
    Send an email using the Flask-Mail setup in fishcore/__init__.py.
    """
    print("🚨 DEBUG: MAIL_USERNAME =", current_app.config.get("MAIL_USERNAME"))
    print("🚨 DEBUG: Sending email to", to)
    msg = Message(
        subject,
        recipients=[to],
        html=html,
        sender=current_app.config["MAIL_DEFAULT_SENDER"]  # ✅ verified sender address
    )
    mail.send(msg)