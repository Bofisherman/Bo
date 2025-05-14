from flask import Flask, render_template
import os


app = Flask(__name__,
            static_folder='frontend/static',
            template_folder='frontend/templates')


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/lessons')
def lessons():
    return render_template('lessons.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/support')
def support():
    return render_template('support.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # use Render's port if defined
    app.run(host="0.0.0.0", port=port)
