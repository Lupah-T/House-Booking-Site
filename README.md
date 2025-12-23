# 🏠 Campus House Booking System

A full-stack web application that allows campus students to book rental houses online, view available rooms, and make payments via M-Pesa, Stripe, or PayPal. Admins and landlords can post new houses with location, price, contact info, and images.

---

## ✨ Features

- 🧑‍🎓 **Student Accounts**
  - Sign up, log in, and book rooms
  - View personal bookings in "My Bookings"
  
- 🏢 **Admin Panel**
  - View all bookings
  - Manage houses (add/delete)

- 🏘️ **Landlord Access**
  - Sign up and log in
  - Post new houses with photos and contact info

- 💰 **Payment Integration**
  - M-Pesa (simulated)
  - Stripe
  - PayPal

- 📧 **Email Confirmation**
  - Sends confirmation email after successful booking

---

## 🛠️ Technologies Used

- **Backend:** Python (Flask)
- **Frontend:** HTML, TailwindCSS
- **Database:** SQLite
- **Auth:** Session-based (Flask Sessions)
- **Password Security:** `werkzeug.security` (Password hashing)
- **Email:** SMTP (Gmail)
- **Payment (Simulated):** M-Pesa, Stripe, PayPal

---

## 🔒 Security & Environment Variables

This application uses a `.env` file for sensitive configuration. **Never commit your `.env` file to GitHub.**

### Required Variables:
- `FLASK_SECRET_KEY`: Used to sign session cookies.
- `SENDER_EMAIL`: Your Gmail address for notifications.
- `SENDER_PASSWORD`: Your Gmail App Password.

### Generating a Secret Key:
If you need a new secret key, run:
```bash
python3 -c 'import secrets; print(secrets.token_hex(24))'
```

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/house-booking-system.git
cd house-booking-system
