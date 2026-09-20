import sqlite3
from datetime import datetime, timedelta
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = "app_database.db"

def get_connection():
    """Connect to SQLite and configure it to return rows as dictionaries."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# =====================================================================
# USER REGISTRATION & AUTHENTICATION
# =====================================================================

def register_user(username, email, password, role="student", school_id=None, grade_level=None):
    """
    Hashes the user password and inserts the new user into the database.
    Returns (True, user_id) on success or (False, error_message).
    """
    hashed_pw = generate_password_hash(password)
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, school_id, grade_level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username.strip(), email.strip().lower(), hashed_pw, role, school_id, grade_level))
        conn.commit()
        return True, cursor.lastrowid
    except sqlite3.IntegrityError as e:
        error = str(e).lower()
        if "username" in error:
            return False, "Username is already taken."
        elif "email" in error:
            return False, "An account with this email already exists."
        return False, "Registration failed due to a database constraint."
    finally:
        conn.close()

def authenticate_user(login_identifier, password):
    """
    Allows login with either username OR email.
    Returns user dict if valid, None if invalid.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, username, email, password_hash, role, school_id 
        FROM users 
        WHERE (LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?))
          AND is_active = 1
    """, (login_identifier.strip(), login_identifier.strip()))
    
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user["password_hash"], password):
        return dict(user)
    return None

# =====================================================================
# FORGOT / RESET PASSWORD SYSTEM
# =====================================================================

def create_password_reset_token(email, expires_in_minutes=15):
    """
    Generates a secure, temporary token for a user and stores it.
    Returns (token, username) if user exists, or None.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, username FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return None
    
    # Generate a cryptographically secure random token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    
    cursor.execute("""
        INSERT INTO password_resets (user_id, token, expires_at)
        VALUES (?, ?, ?)
    """, (user["user_id"], token, expires_at.strftime("%Y-%m-%d %H:%M:%S")))
    
    conn.commit()
    conn.close()
    return token, user["username"]

def reset_password_with_token(token, new_password):
    """
    Validates token expiration and single-use status, then updates the password.
    Returns (True, message) or (False, error_message).
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        SELECT reset_id, user_id, expires_at, used
        FROM password_resets
        WHERE token = ?
    """, (token,))
    
    record = cursor.fetchone()
    if not record:
        conn.close()
        return False, "Invalid reset link."
    if record["used"] == 1:
        conn.close()
        return False, "This reset link has already been used."
    if record["expires_at"] < now_str:
        conn.close()
        return False, "This reset link has expired. Please request a new one."
    
    # Hash new password and update user record
    new_hashed_pw = generate_password_hash(new_password)
    
    cursor.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (new_hashed_pw, record["user_id"]))
    cursor.execute("UPDATE password_resets SET used = 1 WHERE reset_id = ?", (record["reset_id"],))
    
    conn.commit()
    conn.close()
    return True, "Password has been successfully reset."
