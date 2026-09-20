from flask import Flask, request, jsonify, session
import db

app = Flask(__name__)
# Replace this with a secure random secret key in production
app.secret_key = "development-secret-key-replace-later"

# -------------------------------------------------------------
# 1. USER REGISTRATION (Students & Teachers)
# -------------------------------------------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student") # 'student' or 'teacher'
    school_id = data.get("school_id")
    grade_level = data.get("grade_level")
    
    # Simple validation rules
    if not username or not email or not password:
        return jsonify({"success": False, "error": "Username, email, and password are required."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters long."}), 400
    if role not in ["student", "teacher"]:
        return jsonify({"success": False, "error": "Role must be 'student' or 'teacher'."}), 400

    success, result = db.register_user(
        username=username,
        email=email,
        password=password,
        role=role,
        school_id=school_id,
        grade_level=grade_level
    )
    
    if success:
        return jsonify({"success": True, "message": "Account created successfully!", "user_id": result}), 201
    else:
        return jsonify({"success": False, "error": result}), 409

# -------------------------------------------------------------
# 2. USER LOGIN
# -------------------------------------------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    login_identifier = data.get("login_identifier") # Can be username OR email
    password = data.get("password")
    
    if not login_identifier or not password:
        return jsonify({"success": False, "error": "Login and password are required."}), 400

    user = db.authenticate_user(login_identifier, password)
    if not user:
        return jsonify({"success": False, "error": "Invalid username/email or password."}), 401
    
    # Store user identity in the server-side session
    session["user_id"] = user["user_id"]
    session["role"] = user["role"]
    session["username"] = user["username"]

    return jsonify({
        "success": True,
        "message": f"Welcome back, {user['username']}!",
        "user": {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"],
            "email": user["email"]
        }
    }), 200

# -------------------------------------------------------------
# 3. FORGOT PASSWORD (Generate link & simulate email)
# -------------------------------------------------------------
@app.route("/api/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json() or {}
    email = data.get("email")
    
    if not email:
        return jsonify({"success": False, "error": "Email is required."}), 400
    
    result = db.create_password_reset_token(email)
    
    # Generic security message (prevents malicious users from guessing valid emails)
    response_msg = "If an account with that email exists, a password reset link has been generated."
    
    if result:
        token, username = result
        reset_link = f"http://127.0.0.1:5000/reset-password?token={token}"
        
        # In development/local testing, print the link directly to the console:
        print("\n" + "=" * 60)
        print(f"📧 [EMAIL SIMULATOR] To: {email}")
        print(f"Hi {username}, click this link to reset your password (valid 15 mins):")
        print(reset_link)
        print("=" * 60 + "\n")
        
    return jsonify({"success": True, "message": response_msg}), 200

# -------------------------------------------------------------
# 4. RESET PASSWORD WITH TOKEN
# -------------------------------------------------------------
@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json() or {}
    token = data.get("token")
    new_password = data.get("new_password")
    
    if not token or not new_password:
        return jsonify({"success": False, "error": "Token and new password are required."}), 400
    if len(new_password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters long."}), 400

    success, message = db.reset_password_with_token(token, new_password)
    if success:
        return jsonify({"success": True, "message": message}), 200
    else:
        return jsonify({"success": False, "error": message}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
