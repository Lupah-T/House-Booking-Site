from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.secret_key = "your_secret_key"

# ======================== #
# ⚙️ DB INIT
# ======================== #
def init_db():
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()

    # Bookings Table
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

    # Houses Table
    cur.execute('''CREATE TABLE IF NOT EXISTS houses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        location TEXT,
        image_filename TEXT
    )''')

    # Students Table
    cur.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        year INTEGER,
        reg_no TEXT UNIQUE
    )''')

    conn.commit()
    conn.close()

# ======================== #
# 📧 EMAIL CONFIRMATION
# ======================== #
def send_email(to_email, student_name, house_name, checkin):
    sender_email = "isaackash254@gmail.com"
    sender_password = "sc211/4411/2024"  # App password if 2FA

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
# 🌐 ROUTES
# ======================== #

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/house")
def house():
    query = request.args.get("search")
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()

    if query:
        cur.execute("SELECT * FROM houses WHERE location LIKE ?", ('%' + query + '%',))
    else:
        cur.execute("SELECT * FROM houses")
    houses = cur.fetchall()

    cur.execute("SELECT house FROM bookings WHERE paid = 1")
    booked_houses = [row[0] for row in cur.fetchall()]

    conn.close()

    return render_template("house.html", houses=houses, booked=booked_houses, search=query)

@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name = request.form["fullname"]
        phone = request.form["phone"]
        house = request.form["house"]
        checkin = request.form["checkin"]
        duration = request.form["duration"]
        email = request.form["email"]
        reg_no = session.get("student")[3] if session.get("student") else None

        conn = sqlite3.connect("bookings.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO bookings (fullname, phone, house, checkin, duration, paid, reg_no) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (name, phone, house, checkin, duration, 1, reg_no))
        conn.commit()
        conn.close()

        send_email(email, name, house, checkin)
        return redirect(url_for("confirmation", name=name))

    return render_template("booking.html")

@app.route("/confirmation")
def confirmation():
    name = request.args.get("name")
    return render_template("confirmation.html", name=name)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/add-house", methods=["GET", "POST"])
def add_house():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        location = request.form["location"]
        image = request.files["image"]

        filename = None
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

        conn = sqlite3.connect("bookings.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO houses (name, description, location, image_filename) VALUES (?, ?, ?, ?)",
                    (name, description, location, filename))
        conn.commit()
        conn.close()

        return redirect("/house")

    return render_template("add_house.html")

# ======================== #
# 👨‍🎓 STUDENT LOGIN
# ======================== #
@app.route("/student-login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        name = request.form["name"]
        year = request.form["year"]
        reg_no = request.form["reg_no"]

        conn = sqlite3.connect("bookings.db")
        cur = conn.cursor()

        cur.execute("SELECT * FROM students WHERE reg_no = ?", (reg_no,))
        student = cur.fetchone()

        if not student:
            cur.execute("INSERT INTO students (name, year, reg_no) VALUES (?, ?, ?)",
                        (name, year, reg_no))
            conn.commit()
            cur.execute("SELECT * FROM students WHERE reg_no = ?", (reg_no,))
            student = cur.fetchone()

        conn.close()
        session["student"] = student
        return redirect("/student-dashboard")

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
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM bookings WHERE reg_no = ?", (reg_no,))
    bookings = cur.fetchall()
    conn.close()

    return render_template("my_bookings.html", bookings=bookings)

@app.route("/edit-booking/<int:id>", methods=["GET", "POST"])
def edit_booking(id):
    if "student" not in session:
        return redirect("/student-login")

    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()

    if request.method == "POST":
        fullname = request.form["fullname"]
        phone = request.form["phone"]
        checkin = request.form["checkin"]
        duration = request.form["duration"]
        cur.execute("UPDATE bookings SET fullname=?, phone=?, checkin=?, duration=? WHERE id=?",
                    (fullname, phone, checkin, duration, id))
        conn.commit()
        conn.close()
        return redirect("/my-bookings")

    cur.execute("SELECT * FROM bookings WHERE id=?", (id,))
    booking = cur.fetchone()
    conn.close()
    return render_template("edit_booking.html", booking=booking)

@app.route("/delete-booking/<int:id>")
def delete_booking_student(id):
    if "student" not in session:
        return redirect("/student-login")
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM bookings WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/my-bookings")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ======================== #
# 🛡️ ADMIN PANEL
# ======================== #
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin123":
            session["admin"] = True
            return redirect("/admin/dashboard")
        else:
            flash("Invalid credentials", "error")
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/admin")

    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM bookings")
    bookings = cur.fetchall()
    cur.execute("SELECT * FROM houses")
    houses = cur.fetchall()
    conn.close()

    return render_template("admin_dashboard.html", bookings=bookings, houses=houses)

@app.route("/admin/delete-booking/<int:id>")
def delete_booking(id):
    if not session.get("admin"):
        return redirect("/admin")
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM bookings WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin/dashboard")

@app.route("/admin/delete-house/<int:id>")
def delete_house(id):
    if not session.get("admin"):
        return redirect("/admin")
    conn = sqlite3.connect("bookings.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM houses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin/dashboard")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin")

# ======================== #
# ❌ 404 PAGE
# ======================== #
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", path=request.path), 404

# ======================== #
# ▶️ START
# ======================== #
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
