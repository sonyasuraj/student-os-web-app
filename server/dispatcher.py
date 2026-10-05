"""
Flask Dispatcher Server for Rate My Teacher
Routes requests between the browser (Front-End) and the database gateway (Back-End).
"""

import hashlib
import os
import secrets
from flask import Flask, jsonify, render_template, request, session
import db_gateway
import review

# Configure paths to the website folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "website", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "website", "static")

dispatcher = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)
dispatcher.secret_key = "rate-my-teacher-anonymous-development-key"


def get_client_hash():
    """
    Creates or retrieves an anonymous, cryptographic session token.
    Complies with COPPA: no IP addresses, usernames, or cookies with personal data are stored.
    """
    if "anonymous_user_token" not in session:
        session["anonymous_user_token"] = secrets.token_hex(16)
    return hashlib.sha256(session["anonymous_user_token"].encode()).hexdigest()


# ===========================================================================
# 🌐 HTML PAGE ROUTES
# ===========================================================================

@dispatcher.route("/")
def index_page():
    """Main landing page: lists all teachers with optional search and filter."""
    query = request.args.get("q", "")
    department = request.args.get("department", "")
    grade = request.args.get("grade", "")

    teachers = db_gateway.get_all_teachers(query, department, grade)
    schools = db_gateway.get_all_schools()

    return render_template(
        "index.html",
        teachers=teachers,
        schools=schools,
        search_query=query,
        selected_department=department,
        selected_grade=grade
    )


@dispatcher.route("/teacher/<int:teacher_id>")
def teacher_page(teacher_id):
    """Teacher details page: displays profile, rating summary, and review feed."""
    teacher = db_gateway.get_teacher_by_id(teacher_id)
    if not teacher:
        return "<h1>Teacher not found</h1><p><a href='/'>Return to Home</a></p>", 404

    client_hash = get_client_hash()
    reviews = db_gateway.get_teacher_reviews(teacher_id, client_hash)
    available_tags = db_gateway.get_all_tags()

    return render_template(
        "teacher.html",
        teacher=teacher,
        reviews=reviews,
        tags=available_tags,
        has_reviews=len(reviews) > 0
    )


@dispatcher.route("/add-teacher")
def add_teacher_page():
    """Page with the form to add a new teacher profile."""
    schools = db_gateway.get_all_schools()
    return render_template("add_teacher.html", schools=schools)


# ===========================================================================
# 🔌 REST API ENDPOINTS (For JavaScript Fetch / Async Requests)
# ===========================================================================

@dispatcher.route("/api/teachers", methods=["GET"])
def api_get_teachers():
    """API to fetch teachers list as JSON."""
    query = request.args.get("q")
    department = request.args.get("department")
    grade = request.args.get("grade")

    teachers = db_gateway.get_all_teachers(query, department, grade)
    return jsonify({"success": True, "count": len(teachers), "teachers": teachers}), 200


@dispatcher.route("/api/teachers", methods=["POST"])
def api_create_teacher():
    """
    API to create a new teacher.
    Accepts JSON or form data.
    """
    data = request.get_json() if request.is_json else request.form

    school_id = data.get("school_id")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    department = data.get("department")
    grade_level = data.get("grade_level")
    bio = data.get("bio", "")

    success, teacher_id, error = db_gateway.add_teacher(
        school_id, first_name, last_name, department, grade_level, bio
    )

    if not success:
        return jsonify({"success": False, "error": error}), 400

    return jsonify({
        "success": True,
        "message": "Teacher profile created successfully!",
        "teacher_id": teacher_id
    }), 201


@dispatcher.route("/api/teachers/<int:teacher_id>", methods=["GET"])
def api_get_teacher_detail(teacher_id):
    """API to fetch single teacher details."""
    teacher = db_gateway.get_teacher_by_id(teacher_id)
    if not teacher:
        return jsonify({"success": False, "error": "Teacher not found"}), 404
    return jsonify({"success": True, "teacher": teacher}), 200


@dispatcher.route("/api/teachers/<int:teacher_id>/reviews", methods=["GET"])
def api_get_reviews(teacher_id):
    """API to fetch all reviews for a teacher."""
    client_hash = get_client_hash()
    reviews = db_gateway.get_teacher_reviews(teacher_id, client_hash)
    return jsonify({
        "success": True,
        "teacher_id": teacher_id,
        "count": len(reviews),
        "reviews": reviews
    }), 200


@dispatcher.route("/api/teachers/<int:teacher_id>/reviews", methods=["POST"])
def api_submit_review(teacher_id):
    """
    API to submit an anonymous review for a teacher.
    Accepts JSON or form data.
    """
    data = request.get_json() if request.is_json else request.form

    rating_overall = data.get("rating_overall")
    rating_difficulty = data.get("rating_difficulty")
    rating_helpfulness = data.get("rating_helpfulness")
    review_text = data.get("review_text")
    course_name = data.get("course_name")
    reviewer_role = data.get("reviewer_role", "student")
    student_grade_level = data.get("student_grade_level")
    tag_ids = data.get("tag_ids", [])

    client_hash = get_client_hash()

#
# Call reviews.py and pass the inout values from the request
# Comment all input functions in review.py as they were temporary and pass the values sent from dispatcher.py
#
    success, review_id, error = review.save_review(
        teacher_id=teacher_id,
        rating_overall=rating_overall,
        rating_difficulty=rating_difficulty,
        rating_helpfulness=rating_helpfulness,
        review_text=review_text,
        client_fingerprint_hash=client_hash,
        course_name=course_name,
        reviewer_role=reviewer_role,
        student_grade_level=student_grade_level,
        tag_ids=tag_ids
    )

    print ("Final response from server layer. response variables: " + success + ", " + str(review_id) + ", " + str(error))
    if not success:
        return jsonify({"success": False, "error": error}), 400

    return jsonify({
        "success": True,
        "message": "Thank you! Your anonymous review has been posted.",
        "review_id": review_id
    }), 201


@dispatcher.route("/api/schools", methods=["GET"])
def api_get_schools():
    """API to fetch all schools."""
    schools = db_gateway.get_all_schools()
    return jsonify({"success": True, "schools": schools}), 200


@dispatcher.route("/api/tags", methods=["GET"])
def api_get_tags():
    """API to fetch all pre-defined tags."""
    tags = db_gateway.get_all_tags()
    return jsonify({"success": True, "tags": tags}), 200


# ===========================================================================
# 🏁 APPLICATION ENTRY POINT
# ===========================================================================

if __name__ == "__main__":
    print("🚀 Rate My Teacher Web Server running at http://127.0.0.1:5000")
    dispatcher.run(debug=True, port=5000)