import os
import sqlite3
from flask import Blueprint, render_template, request, redirect, session, url_for, flash, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from flask_mail import Message
from fishcore.classifier.fish_classifier import classify_fish
from fishcore import mail
from fishcore.config import Config

main_routes = Blueprint('main', __name__)

# === Helpers ===
def get_db_connection():
    conn = sqlite3.connect('videos.db')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# === Routes ===


@main_routes.route('/')
def home():
    return render_template("home.html")

# Define your other routes (register, login, contact, etc.) here like you already have

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_db_connection():
    conn = sqlite3.connect('videos.db')
    conn.row_factory = sqlite3.Row
    return conn
@main_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash("Registered successfully. You can now log in.", "success")
        except sqlite3.IntegrityError:
            flash("Username already exists.", "error")
            return redirect('/register')
        finally:
            conn.close()

        return redirect('/login')
    return render_template('register.html')

@main_routes.route('/debug_session')
def debug_session():
    from flask import jsonify
    return jsonify(dict(session))

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        # Log input to debug iPhone issues
        print(f"Username input (raw): [{username.encode('utf-8')}]")
        print(f"Password input (raw): [{password_input.encode('utf-8')}]")

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password_input):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']

            return redirect('/admin/categories' if user['is_admin'] else '/lessons')

        # ✅ Show error if login fails
        flash("Invalid username or password", "error")
        return redirect('/login')

    return render_template('login.html')


@main_routes.route('/logout')
def logout():
    session.clear()
    return redirect('/')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Login required to access this page.", "error")
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function


@main_routes.route('/lessons')
@login_required
def lessons():
    conn = get_db_connection()

    categories = conn.execute("SELECT * FROM categories ORDER BY display_order, name").fetchall()

    category_lessons = {}
    for cat in categories:
        lessons = conn.execute("SELECT * FROM lessons WHERE category_id = ?", (cat['id'],)).fetchall()
        category_lessons[cat['id']] = lessons

    conn.close()

    return render_template('lessons.html', categories=categories, category_lessons=category_lessons)
@main_routes.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        print(f"Got message from {name} <{email}>: {message}")  # 👈 log to console

        msg = Message(
            subject=f"Message from {name}",
            recipients=["captainliangbo@gmail.com"],  # Where YOU want to receive it
            body=f"From: {name} <{email}>\n\n{message}"
        )

        try:
            mail.send(msg)
            flash("Message sent successfully!", "success")
        except Exception as e:
            print("Email failed:", e)
            flash("There was a problem sending your message.", "error")

        return redirect('/contact')

    return render_template('contact.html')


@main_routes.route('/support')
def support():
    return render_template('support.html')
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash("Admin access required.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@main_routes.route('/admin/upload', methods=['GET', 'POST'])
@admin_required
def upload_lesson():
    conn = get_db_connection()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        media_type = request.form['media_type']
        category_id = request.form['category']
        file = request.files.get('media')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            folder = 'videos' if media_type == 'video' else 'images'
            upload_path = os.path.join(current_app.static_folder, folder)  # ✅ Safe and dynamic

            os.makedirs(upload_path, exist_ok=True)
            filepath = os.path.join(upload_path, filename)
            file.save(filepath)

            media_url = url_for('static', filename=f"{folder}/{filename}")

            conn.execute(
                '''INSERT INTO lessons (title, description, media_type, media_url, category_id, uploaded_by)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (title, description, media_type, media_url, category_id, session['username'])
            )
            conn.commit()
            flash("Lesson uploaded successfully.", "success")
        else:
            flash("Invalid file or missing input.", "error")

    # Fetch categories for dropdown
    categories = conn.execute("SELECT * FROM categories ORDER BY display_order, name").fetchall()
    conn.close()
    return render_template('admin_upload.html', categories=categories)
@main_routes.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def manage_categories():
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        icon = request.form.get('icon', '')

        conn.execute(
            "INSERT INTO categories (name, description, icon) VALUES (?, ?, ?)",
            (name, description, icon)
        )
        conn.commit()
        flash("Category added successfully.", "success")

    categories = conn.execute("SELECT * FROM categories ORDER BY display_order ASC, id ASC").fetchall()
    conn.close()
    return render_template('admin_categories.html', categories=categories)
@main_routes.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories ORDER BY display_order, name").fetchall()

    category_lessons = {}
    for cat in categories:
        lessons = conn.execute("SELECT * FROM lessons WHERE category_id = ? ORDER BY created_at DESC", (cat['id'],)).fetchall()
        category_lessons[cat['id']] = lessons

    conn.close()
    return render_template('admin_dashboard.html', categories=categories, category_lessons=category_lessons)
@main_routes.route('/identify', methods=['GET', 'POST'])
def identify_fish():
    if request.method == 'POST':
        image = request.files.get('image')
        if not image:
            flash("Please upload a valid image file.", "error")
            return redirect('/')
        try:
            result = classify_fish(image)
            return render_template("result.html", result=result)
        except Exception as e:
            print(f"[ERROR] Classification failed: {e}")
            flash("Something went wrong while classifying the image.", "error")
            return redirect('/')
    return redirect('/')

