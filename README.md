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

⚠️ Note: The original app.py file was removed from this repository to prevent exposing sensitive configuration details. A sanitized version may be re-uploaded later with environment variables and secure best practices in place.

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/house-booking-system.git
cd house-booking-system
