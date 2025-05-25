from flask import Blueprint, render_template, request, redirect, session, url_for, flash, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from flask_mail import Message
from fishcore.classifier.fish_classifier import classify_fish
from fishcore import mail
from fishcore.config import Config
from fishcore.db import get_db
from fishcore.models import User, Category, Lesson
from utils.s3_upload import upload_file_to_s3
import re
from dotenv import load_dotenv
import os

load_dotenv()
main_routes = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main_routes.route('/')
def home():
    return render_template("home.html", lessons=lessons)

@main_routes.route('/register', methods=['GET', 'POST'])
def register():
    db = next(get_db())
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        email_regex = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(email_regex, email):
            flash("Please enter a valid email address.", "error")
            return redirect('/register')

        if db.query(User).filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect('/register')

        hashed_pw = generate_password_hash(password)
        new_user = User(email=email, password=hashed_pw)
        db.add(new_user)
        db.commit()

        flash("Registered successfully. You can now log in.", "success")
        return redirect('/login')

    return render_template('register.html')


@main_routes.route('/debug_session')
def debug_session():
    return jsonify(dict(session))

from flask_dance.contrib.google import google
from fishcore.models import User
from fishcore.db import get_db
from werkzeug.security import generate_password_hash

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    db = next(get_db())

    if request.method == 'POST':
        email = request.form.get('email')
        password_input = request.form.get('password')

        user = db.query(User).filter_by(email=email).first()

        if user and check_password_hash(user.password, password_input):
            session['user_id'] = user.id
            session['email'] = user.email
            session['is_admin'] = user.is_admin
            flash("Welcome back!", "success")
            return redirect('/admin/categories' if user.is_admin else '/lessons')

        flash("Invalid email or password", "error")
        return redirect('/login')

    return render_template('login.html')
@main_routes.route("/login/google")
def google_login():
    db = next(get_db())

    # If user not yet authorized, start Google login flow
    if not google.authorized:
        return redirect(url_for("google.login"))

    # Get user info from Google
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Failed to fetch user info from Google.", "error")
        return redirect(url_for("main.login"))

    user_info = resp.json()
    email = user_info.get("email")

    if not email:
        flash("Google account did not return an email address.", "error")
        return redirect(url_for("main.login"))

    # Check if user already exists
    user = db.query(User).filter_by(username=email).first()
    if not user:
        user = User(
            username=email,
            password=generate_password_hash("google-oauth-placeholder"),  # prevent password login
            is_admin=False
        )
        db.add(user)
        db.commit()

    # Log user in by setting session
    session["user_id"] = user.id
    session["username"] = user.username
    session["is_admin"] = user.is_admin

    flash("Logged in with Google!", "success")
    return redirect("/admin/categories" if user.is_admin else "/lessons")

@main_routes.route("/login/apple")
def apple_login():
    flash("Apple login is not available yet. Coming soon!", "error")
    return redirect(url_for("main.login"))

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
    db = next(get_db())
    categories = db.query(Category).order_by(Category.display_order, Category.name).all()
    category_lessons = {
        cat.id: db.query(Lesson).filter_by(category_id=cat.id).all() for cat in categories
    }
    return render_template('lessons.html', categories=categories, category_lessons=category_lessons)

@main_routes.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        msg = Message(
            subject=f"Message from {name}",
            recipients=["captainliangbo@gmail.com"],
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
    db = next(get_db())
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        media_type = request.form['media_type']
        category_id = request.form['category']
        file = request.files.get('media')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            folder = 'videos' if media_type == 'video' else 'images'

            try:
                media_url = upload_file_to_s3(file, filename, folder=folder)
            except Exception as e:
                flash(f"Upload failed: {e}", "error")
                return redirect('/admin/upload')

            lesson = Lesson(title=title, description=description, media_type=media_type,
                            media_url=media_url, category_id=category_id, uploaded_by=session['username'])
            db.add(lesson)
            db.commit()
            flash("Lesson uploaded successfully.", "success")
        else:
            flash("Invalid file or missing input.", "error")

    categories = db.query(Category).order_by(Category.display_order, Category.name).all()
    return render_template('admin_upload.html', categories=categories)

@main_routes.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def manage_categories():
    db = next(get_db())
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        icon = request.form.get('icon', '')

        category = Category(name=name, description=description, icon=icon)
        db.add(category)
        db.commit()
        flash("Category added successfully.", "success")

    categories = db.query(Category).order_by(Category.display_order, Category.id).all()
    return render_template('admin_categories.html', categories=categories)

@main_routes.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = next(get_db())
    categories = db.query(Category).order_by(Category.display_order, Category.name).all()
    category_lessons = {
        cat.id: db.query(Lesson).filter_by(category_id=cat.id).order_by(Lesson.created_at.desc()).all()
        for cat in categories
    }
    return render_template('admin_dashboard.html', categories=categories, category_lessons=category_lessons)

@main_routes.route('/admin/category/edit', methods=['POST'])
@admin_required
def edit_category():
    db = next(get_db())
    category_id = request.form['category_id']
    name = request.form['name']
    description = request.form.get('description', '')
    icon = request.form.get('icon', '')

    category = db.query(Category).get(category_id)
    if category:
        category.name = name
        category.description = description
        category.icon = icon
        db.commit()
        flash("Category updated successfully.", "success")
    return redirect(url_for('main.admin_dashboard'))

@main_routes.route('/admin/lesson/edit', methods=['POST'])
@admin_required
def edit_lesson():
    db = next(get_db())
    lesson_id = request.form['lesson_id']
    title = request.form['title']
    description = request.form['description']
    media_type = request.form['media_type']
    file = request.files.get('media')

    lesson = db.query(Lesson).get(lesson_id)
    if not lesson:
        flash("Lesson not found.", "error")
        return redirect(url_for('main.admin_dashboard'))

    lesson.title = title
    lesson.description = description
    lesson.media_type = media_type

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        folder = 'videos' if media_type == 'video' else 'images'
        try:
            media_url = upload_file_to_s3(file, filename, folder=folder)
            lesson.media_url = media_url
        except Exception as e:
            flash(f"Upload failed: {e}", "error")
            return redirect(url_for('main.admin_dashboard'))

    db.commit()
    flash("Lesson updated successfully.", "success")
    return redirect(url_for('main.admin_dashboard'))

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

@main_routes.route('/admin/category/delete', methods=['POST'])
@admin_required
def delete_category():
    db = next(get_db())
    category_id = request.form['category_id']
    db.query(Lesson).filter_by(category_id=category_id).delete()
    db.query(Category).filter_by(id=category_id).delete()
    db.commit()
    flash("Category and all related lessons deleted.", "success")
    return redirect(url_for('main.admin_dashboard'))

@main_routes.route('/admin/lesson/delete', methods=['POST'])
@admin_required
def delete_lesson():
    db = next(get_db())
    lesson_id = request.form['lesson_id']
    db.query(Lesson).filter_by(id=lesson_id).delete()
    db.commit()
    flash("Lesson deleted successfully.", "success")
    return redirect(url_for('main.admin_dashboard'))

@main_routes.route('/blog')
def blog():
    # Sample static blog entries
    blog_posts = [
        {
            "title": "Perfecting Casting Techniques",
            "slug": "perfecting-casting-techniques",
            "date": "Oct 10, 2023",
            "summary": "Uncover detailed strategies to enhance your casting skills for better fishing outcomes.",
            "image": url_for('static', filename='images/d3a796d5-e4df-460e-8804-1618d4d018a9.avif')
        },
        # Add more blog entries here
    ]
    return render_template("blog.html", posts=blog_posts)


@main_routes.route('/blog/<slug>')
def blog_post(slug):
    # Simulated blog lookup
    sample_blog = {
        "perfecting-casting-techniques": {
            "title": "Perfecting Casting Techniques",
            "date": "Oct 10, 2023",
            "image": url_for('static', filename='images/d3a796d5-e4df-460e-8804-1618d4d018a9.avif'),
            "content": """
                <p>Casting is one of the most essential skills in fishing...</p>
                <p>Here are 3 techniques that pros use every time:</p>
                <ul>
                    <li>Use your wrist, not your elbow</li>
                    <li>Keep your eyes on the landing zone</li>
                    <li>Let the rod do the work</li>
                </ul>
            """
        }
    }

    post = sample_blog.get(slug)
    if not post:
        flash("Blog post not found.", "error")
        return redirect(url_for('blog'))

    return render_template("blog_post.html", post_title=post['title'],
                           post_date=post['date'],
                           post_image=post['image'],
                           post_content=post['content'])

@main_routes.route('/about')
def about():
    return render_template('about.html')

@main_routes.route('/store')
def store():
    return render_template('store.html')  # Or a temporary page
@main_routes.route('/faq')
def faq():
    return render_template('faq.html')
@main_routes.route('/profile')
@login_required
def profile():
    db = next(get_db())
    user = db.query(User).get(session['user_id'])
    lessons = db.query(Lesson).filter_by(uploaded_by=user.email).all()
    return render_template('profile.html', user=user, lessons=lessons)

@main_routes.route('/upload_profile_picture', methods=['POST'])
@login_required
def upload_profile_picture():
    db = next(get_db())
    file = request.files.get('profile_picture')
    if file:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        user = db.query(User).get(session['user_id'])
        user.profile_picture = filename
        db.commit()

        flash("Profile picture updated!", "success")
    else:
        flash("No file selected.", "error")

    return redirect(url_for('main.profile'))

@main_routes.route('/edit_profile')
@login_required
def edit_profile():
    db = next(get_db())
    user = db.query(User).get(session['user_id'])
    return render_template('edit_profile.html', user=user)


@main_routes.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    db = next(get_db())
    user = db.query(User).get(session['user_id'])

    user.birthdate = request.form.get('birthdate')  # already a string
    user.phone = request.form.get('phone')
    user.city = request.form.get('city')
    user.country = request.form.get('country')
    user.bio = request.form.get('bio')  # Now it works

    file = request.files.get('profile_picture')
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))
        user.profile_picture = filename

    db.commit()
    flash("Profile updated successfully.", "success")
    return redirect(url_for('main.profile'))
