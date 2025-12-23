# Deployment Procedure

This document outlines the steps to deploy the House Booking Site to Vercel and Render.

## Prerequisites
1.  **GitHub Repository**: Your code is already pushed to `https://github.com/Lupah-T/House-Booking-Site.git`.
2.  **Accounts**: Ensure you have accounts on [Vercel](https://vercel.com) and [Render](https://render.com).

---

## 🚀 Option 1: Deploy to Render (Recommended for Backend)
Render is ideal for persistent Flask applications.

1.  **New Web Service**:
    - Log in to Render and click **New > Web Service**.
    - Connect your GitHub repository: `Lupah-T/House-Booking-Site`.
2. **Configuration**:
    - **Name**: `house-booking-site`
    - **Environment**: `Python 3`
    - **Region**: Choose the one closest to you.
    - **Branch**: `main`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `gunicorn app:app`
3. **Environment Variables**:
    - Click **Advanced > Add Environment Variable**.
    - `FLASK_SECRET_KEY`: (Your secret key)
    - `SENDER_EMAIL`: (Your SMTP email)
    - `SENDER_PASSWORD`: (Your SMTP password/app password)
    - **Port Configuration**: Removed the hardcoded port 3000 requirement to allow host platforms (Render/Vercel) to manage the port dynamically.
4.  **Deploy**: Click **Create Web Service**.

---

## ⚡ Option 2: Deploy to Vercel
Vercel is great for fast previews but has limitations with persistent databases like SQLite.

1.  **Import Project**:
    - Go to your Vercel Dashboard and click **Add New > Project**.
    - Import `Lupah-T/House-Booking-Site`.
2.  **Configure Project**:
    - Framework Preset: `Other` (Vercel will detect `vercel.json`).
3.  **Environment Variables**:
    - Add `FLASK_SECRET_KEY`, `SENDER_EMAIL`, and `SENDER_PASSWORD` in the **Environment Variables** section.
4.  **Deploy**: Click **Deploy**.

> [!WARNING]
> **Database Persistence**: SQLite (`bookings.db`) will reset on every Vercel deployment if not using an external database. For persistent data, use **Render** or connect a external SQL database (like PostgreSQL).

---

## 🛠️ Local Execution
To run the app locally on your machine:
```bash
python3 app.py
```
The app will be accessible at `http://localhost:3000`.
