from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import random
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key")

# Email Configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")

mail = Mail(app)

# File to store user data
DB_FILE = "users.json"

# Function to load users from a JSON file
def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as file:
            return json.load(file)
    return {}

# Function to save users to a JSON file
def save_users():
    with open(DB_FILE, "w") as file:
        json.dump(users, file)

# Load users into memory
users = load_users()

# Home Route
@app.route('/')
def home():
    if 'email' in session:
        return f"Welcome {session['email']}! <br><a href='/logout'>Logout</a>"
    return render_template('login.html')

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if email in users:
            flash("Email already registered! Try logging in.", "error")
        else:
            users[email] = password
            save_users()  # Save data persistently
            flash("Signup successful! You can now log in.", "success")
            return redirect(url_for('home'))

    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email'].strip().lower()
    password = request.form['password']

    print("Login attempt with email:", email)  # Debugging
    print("Stored emails:", users.keys())  # Debugging

    if email in users and users[email] == password:
        session['email'] = email
        return redirect(url_for('home'))
    else:
        flash("Invalid Email or Password!", "error")
        return redirect(url_for('home'))
# Welcome route
@app.route('/welcome')
def welcome():
    if 'email' in session:
        return render_template('welcome.html', email=session['email'])
    return redirect(url_for('home'))

# Forgot Password Route
@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()

        print("Password reset request for:", email)  # Debugging

        if email in users:
            verification_code = str(random.randint(100000, 999999))
            session['reset_code'] = verification_code
            session['reset_email'] = email

            try:
                msg = Message("Password Reset Code", sender=app.config["MAIL_USERNAME"], recipients=[email])
                msg.body = f"Your password reset verification code is: {verification_code}"
                mail.send(msg)
                flash("A verification code has been sent to your email.", "info")
            except Exception as e:
                flash(f"Error sending email: {str(e)}", "error")

            return redirect(url_for('reset_password'))
        else:
            flash("Email not found!", "error")

    return render_template('forgot.html')

# Reset Password Route
@app.route('/reset', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        code = request.form['code']
        new_password = request.form['new_password']

        if 'reset_code' in session and session['reset_code'] == code:
            email = session['reset_email']
            users[email] = new_password
            save_users()  # Save updated password persistently
            session.pop('reset_code', None)
            session.pop('reset_email', None)

            flash("Password reset successful! You can now log in.", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid verification code!", "error")

    return render_template('reset.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
 