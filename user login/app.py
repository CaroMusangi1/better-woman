from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Email Configuration (Use your email credentials)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "your_email@gmail.com"
app.config["MAIL_PASSWORD"] = "your_email_password"

mail = Mail(app)

# Fake database (Replace with a real database)
users = {}

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
        email = request.form['email']
        password = request.form['password']
        
        if email in users:
            flash("Email already registered! Try logging in.", "error")
        else:
            users[email] = password
            flash("Signup successful! You can now log in.", "success")
            return redirect(url_for('home'))

    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    if email in users and users[email] == password:
        session['email'] = email
        return redirect(url_for('home'))
    else:
        flash("Invalid Email or Password!", "error")
        return redirect(url_for('home'))

# Forgot Password Route
@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        if email in users:
            verification_code = str(random.randint(100000, 999999))
            session['reset_code'] = verification_code
            session['reset_email'] = email
            
            msg = Message("Password Reset Code", sender="your_email@gmail.com", recipients=[email])
            msg.body = f"Your password reset verification code is: {verification_code}"
            mail.send(msg)

            flash("A verification code has been sent to your email.", "info")
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

if __name__ == '__main_p_':
    app.run(debug=True)