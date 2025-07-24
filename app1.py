from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret")

DATABASE = "bookings.db"

# ===================== DB INIT =====================
def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT,
        phone TEXT,
        house TEXT,
        checkin TEXT,
        duration INTEGER,
        paid INTEGER DEFAULT 0,
        reg_no TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS houses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        location TEXT,
        price TEXT,
        house_type TEXT,
        contact TEXT,
        image_filename TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        year INTEGER,
        reg_no TEXT UNIQUE,
        password TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS landlords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')

    conn.commit()
    conn.close()

# ===================== EMAIL FUNCTION =====================
def send_email(to_email, student_name, house_name, checkin):
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("Email config not set")
        return

    subject = "Booking Confirmation"
    body = f"Hello {student_name},\n\nYou have successfully booked {house_name}.\nCheck-in: {checkin}\n\nThank you!"

    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = to_email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        print("✅ Email sent to", to_email)
    except Exception as e:
        print("❌ Email failed:", e)

# ===================== ROUTES =====================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        data = request.form
        house = f"{data['house_type']} in {data['location']}"
        reg_no = session.get("student")[3] if session.get("student") else None

        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("""INSERT INTO bookings (fullname, phone, house, checkin, duration, paid, reg_no)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (data["fullname"], data["phone"], house, data["checkin"], data["duration"], 1, reg_no))
        conn.commit()
        conn.close()

        send_email(data["email"], data["fullname"], house, data["checkin"])
        return redirect(url_for("confirmation", name=data["fullname"]))
    return render_template("booking.html")

@app.route("/confirmation")
def confirmation():
    name = request.args.get("name")
    return render_template("confirmation.html", name=name)

# ===================== AUTH ROUTES (Example) =====================
@app.route("/student-signup", methods=["GET", "POST"])
def student_signup():
    if request.method == "POST":
        name = request.form["name"]
        year = request.form["year"]
        reg_no = request.form["reg_no"]
        password = request.form["password"]

        hashed = generate_password_hash(password)
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE reg_no=?", (reg_no,))
        if cur.fetchone():
            flash("Student already exists", "error")
            return redirect("/student-login")

        cur.execute("INSERT INTO students (name, year, reg_no, password) VALUES (?, ?, ?, ?)",
                    (name, year, reg_no, hashed))
        conn.commit()
        conn.close()
        flash("Registered successfully", "success")
        return redirect("/student-login")
    return render_template("student_signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ===================== RUN =====================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
