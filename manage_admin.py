import sqlite3
import os
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

DATABASE = os.getenv("DATABASE_URL", "bookings.db")

def create_admin(email, username, password):
    hashed_pw = generate_password_hash(password)
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    
    try:
        cur.execute("INSERT INTO admins (email, username, password) VALUES (?, ?, ?)", 
                    (email, username, hashed_pw))
        db.commit()
        print(f"✅ Admin {username} created successfully.")
    except sqlite3.IntegrityError:
        print(f"❌ Admin with email {email} or username {username} already exists.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("--- CampusRooms Admin Management ---")
    email = input("Enter admin email: ")
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    
    create_admin(email, username, password)
