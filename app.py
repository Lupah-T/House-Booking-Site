from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from dotenv import load_dotenv
from flask import g

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-secret-key")
app.config['UPLOAD_FOLDER'] = 'static/images'
DATABASE = os.getenv("DATABASE_URL", "bookings.db")

# ======================== #
# DB INIT
# ======================== #
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cur = db.cursor()

        # Bookings Table
        cur.execute('''CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT,
            phone TEXT,
            house TEXT,
            checkin TEXT,
            duration INTEGER,
            paid INTEGER DEFAULT 0,
            reg_no TEXT,
            status TEXT DEFAULT 'Pending'
        )''')

        # Houses Table
        cur.execute('''CREATE TABLE IF NOT EXISTS houses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            location TEXT,
            price TEXT,
            house_type TEXT,
            contact TEXT,
            image_filename TEXT,
            availability TEXT DEFAULT 'Vacant'
        )''')

        # Students Table
        cur.execute('''CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            year INTEGER,
            reg_no TEXT UNIQUE,
            password TEXT
        )''')

        # Admins Table
        cur.execute('''CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            password TEXT
        )''')

        # Landlords Table
        cur.execute('''CREATE TABLE IF NOT EXISTS landlords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            password TEXT
        )''')

        db.commit()

# ======================== #
# EMAIL CONFIRMATION
# ======================== #
def send_email(to_email, student_name, house_name, checkin):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

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

# ======================== #
# ROUTES
# ======================== #
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/house")
def house():
    query = request.args.get("search")
    house_type = request.args.get("type")
    location = request.args.get("location")
    db = get_db()
    cur = db.cursor()

    sql = "SELECT * FROM houses WHERE 1=1"
    params = []

    if query:
        sql += " AND (location LIKE ? OR name LIKE ?)"
        params.extend(['%' + query + '%', '%' + query + '%'])
    
    if house_type and house_type != "Any":
        sql += " AND house_type = ?"
        params.append(house_type)

    if location and location != "Any":
        sql += " AND location = ?"
        params.append(location)
        
    cur.execute(sql, params)
    houses = cur.fetchall()

    return render_template("house.html", houses=houses, search=query, current_type=house_type, current_location=location)

@app.route("/booking", methods=["GET", "POST"])
def booking():
    house_id = request.args.get("house_id")
    db = get_db()
    cur = db.cursor()
    selected_house = None
    if house_id:
        cur.execute("SELECT * FROM houses WHERE id = ?", (house_id,))
        selected_house = cur.fetchone()

    if request.method == "POST":
        name = request.form["fullname"]
        phone = request.form["phone"]
        email = request.form["email"]
        checkin = request.form["checkin"]
        duration = request.form["duration"]
        mpesa_code = request.form["mpesa_code"]
        
        # Determine house name and landlord info
        house_name = request.form.get("house_name", "Unknown House")
        house_id_post = request.form.get("house_id")

        cur.execute("""INSERT INTO bookings (fullname, phone, house, checkin, duration, paid, reg_no, status, mpesa_code)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (name, phone, house_name, checkin, duration, 1, session.get("student")["reg_no"] if session.get("student") else None, 'Confirmed', mpesa_code))
        
        # Update house availability to 'Booked'
        if house_id_post:
            cur.execute("UPDATE houses SET availability = 'Booked' WHERE id = ?", (house_id_post,))
        else:
            cur.execute("UPDATE houses SET availability = 'Booked' WHERE name = ?", (house_name,))
        
        db.commit()

        # Notifications
        send_email(email, name, house_name, checkin) # To Student
        
        admin_email = os.getenv("SENDER_EMAIL")
        if admin_email:
            # Alert Admin & Landlord (In this demo, we use the same mailer logic)
            msg_body = f"New Booking: {house_name}\nStudent: {name}\nContact: {phone}\nM-Pesa: {mpesa_code}"
            send_email(admin_email, "Admin/Landlord", house_name, f"{checkin}\n\n{msg_body}")

        flash("Booking successful! Verification in progress.", "success")
        return redirect(url_for("confirmation", name=name))

    return render_template("booking.html", house=selected_house)

@app.route("/confirmation")
def confirmation():
    name = request.args.get("name")
    return render_template("confirmation.html", name=name)

# ======================== #
# ADD HOUSE (Admin/Landlord)
# ======================== #
@app.route("/add-house", methods=["GET", "POST"])
def add_house():
    if "admin" not in session and "landlord" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        location = request.form["location"]
        price = request.form["price"]
        house_type = request.form["house_type"]
        contact = request.form["contact"]
        image = request.files["image"]

        filename = None
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

        db = get_db()
        cur = db.cursor()
        cur.execute("""INSERT INTO houses (name, description, location, price, house_type, contact, image_filename)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (name, description, location, price, house_type, contact, filename))
        db.commit()
        return redirect("/house")

    return render_template("add_house.html")

# ======================== #
# STUDENT AUTH
# ======================== #
@app.route("/student-signup", methods=["GET", "POST"])
def student_signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        year = request.form["year"]
        reg_no = request.form["reg_no"]
        password = request.form["password"]

        hashed = generate_password_hash(password)
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE email=? OR reg_no=?", (email, reg_no))
        existing = cur.fetchone()
        if existing:
            flash("Student with this email or reg no already exists", "error")
            return redirect("/student-login")

        cur.execute("INSERT INTO students (name, email, year, reg_no, password) VALUES (?, ?, ?, ?, ?)",
                    (name, email, year, reg_no, hashed))
        db.commit()
        flash("Registered successfully!", "success")
        return redirect("/student-login")
    return render_template("student_signup.html")

@app.route("/student-login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM students WHERE email=?", (email,))
        student = cur.fetchone()
        if student and check_password_hash(student['password'], password):
            session["student"] = dict(student)
            return redirect("/student-dashboard")
        else:
            flash("Invalid credentials", "error")
    return render_template("student_login.html")

@app.route("/student-dashboard")
def student_dashboard():
    if "student" not in session:
        return redirect("/student-login")
    return render_template("student_dashboard.html", student=session["student"])

@app.route("/my-bookings")
def my_bookings():
    if "student" not in session:
        return redirect("/student-login")

    reg_no = session["student"][3]
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM bookings WHERE reg_no = ?", (reg_no,))
    bookings = cur.fetchall()

    return render_template("my_bookings.html", bookings=bookings)

# ======================== #
# ADMIN AUTH
# ======================== #
@app.route("/admin-signup", methods=["GET", "POST"])
def admin_signup():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        hashed = generate_password_hash(password)

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM admins WHERE email = ? OR username = ?", (email, username))
        if cur.fetchone():
            flash("Admin with this email or username already exists", "error")
            return redirect("/admin")
        cur.execute("INSERT INTO admins (email, username, password) VALUES (?, ?, ?)", (email, username, hashed))
        db.commit()
        flash("Admin created. Login now.", "success")
        return redirect("/admin")
    return render_template("admin_signup.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM admins WHERE email=?", (email,))
        admin = cur.fetchone()
        if admin and check_password_hash(admin['password'], password):
            session["admin"] = dict(admin)
            return redirect("/admin/dashboard")
        else:
            flash("Invalid login", "error")
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin")
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM bookings")
    bookings = cur.fetchall()
    cur.execute("SELECT * FROM houses")
    houses = cur.fetchall()
    return render_template("admin_dashboard.html", bookings=bookings, houses=houses)

# ======================== #
# LANDLORD AUTH
# ======================== #
@app.route("/landlord-signup", methods=["GET", "POST"])
def landlord_signup():
    if "admin" not in session:
        flash("Access denied. Only admins can register landlords.", "error")
        return redirect("/admin")

    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM landlords WHERE email=? OR username=?", (email, username))
        if cur.fetchone():
            flash("Landlord with this email or username already exists", "error")
            return redirect("/admin/dashboard")
        cur.execute("INSERT INTO landlords (email, username, password) VALUES (?, ?, ?)", (email, username, password))
        db.commit()
        flash("Landlord registered successfully", "success")
        return redirect("/admin/dashboard")
    return render_template("landlord_signup.html")

@app.route("/landlord-login", methods=["GET", "POST"])
def landlord_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM landlords WHERE email=?", (email,))
        landlord = cur.fetchone()
        if landlord and check_password_hash(landlord['password'], password):
            session["landlord"] = dict(landlord)
            return redirect("/add-house")
        else:
            flash("Invalid credentials", "error")
    return render_template("landlord_login.html")

# ======================== #
# LOGOUT
# ======================== #
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/admin/delete-booking/<int:id>")
def admin_delete_booking(id):
    if "admin" not in session:
        return redirect("/admin")
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM bookings WHERE id=?", (id,))
    db.commit()
    return redirect("/admin/dashboard")


@app.route("/admin/delete-house/<int:id>")
def admin_delete_house(id):
    if "admin" not in session:
        return redirect("/admin")
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM houses WHERE id=?", (id,))
    db.commit()
    return redirect("/admin/dashboard")


# ======================== #
# RUN
# ======================== #

# Initialize DB when the module is loaded
with app.app_context():
    init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

