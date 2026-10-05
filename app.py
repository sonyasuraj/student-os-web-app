



from flask import Flask, jsonify, request, send_from_directory, session
import sqlite3
import os
import hashlib
import secrets

app = Flask(__name__)
app.secret_key = "rate-my-teacher-anonymous-development-key"

# ============================================================
# DATABASE
# ============================================================

DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "rmt.db"
)


def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON;")
    return db


def get_client_hash():
    """Create a random anonymous browser token and hash it for review rate-limiting."""
    if "anonymous_user_token" not in session:
        session["anonymous_user_token"] = secrets.token_hex(16)
    return hashlib.sha256(session["anonymous_user_token"].encode()).hexdigest()


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return send_from_directory(
        os.path.dirname(__file__),
        "index.html"
    )


# ============================================================
# TEACHER PROFILE PAGE
# ============================================================

@app.route("/teacher.html")
def teacher_page():
    return send_from_directory(
        os.path.dirname(__file__),
        "teacher.html"
    )


# ============================================================
# OLD FRONTEND
# ============================================================

@app.route("/RMT-FRONTEND.html")
def old_frontend():
    return send_from_directory(
        os.path.dirname(__file__),
        "RMT-FRONTEND.html"
    )


# ============================================================
# GET SCHOOLS
# ============================================================

@app.route("/api/schools")
def schools():

    db = get_db()

    rows = db.execute("""
        SELECT
            school_id,
            name,
            school_level,
            district,
            city,
            state,
            zip_code
        FROM schools
        ORDER BY name
    """).fetchall()

    db.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# GET STATES
# ============================================================

@app.route("/api/states")
def states():

    db = get_db()

    rows = db.execute("""
        SELECT DISTINCT state
        FROM schools
        WHERE state IS NOT NULL
        ORDER BY state
    """).fetchall()

    db.close()

    return jsonify([
        row["state"]
        for row in rows
    ])


# ============================================================
# GET DISTRICTS
# ============================================================

@app.route("/api/districts")
def districts():

    state = request.args.get("state", "").strip()

    db = get_db()

    if state:
        rows = db.execute("""
            SELECT DISTINCT district
            FROM schools
            WHERE state = ?
            AND district IS NOT NULL
            ORDER BY district
        """, (state,)).fetchall()

    else:
        rows = db.execute("""
            SELECT DISTINCT district
            FROM schools
            WHERE district IS NOT NULL
            ORDER BY district
        """).fetchall()

    db.close()

    return jsonify([
        row["district"]
        for row in rows
    ])


# ============================================================
# GET SCHOOLS FOR STATE + DISTRICT
# ============================================================

@app.route("/api/school-options")
def school_options():

    state = request.args.get("state", "").strip()
    district = request.args.get("district", "").strip()

    db = get_db()

    query = """
        SELECT
            school_id,
            name,
            school_level,
            district,
            city,
            state
        FROM schools
        WHERE 1 = 1
    """

    params = []

    if state:
        query += " AND state = ?"
        params.append(state)

    if district:
        query += " AND district = ?"
        params.append(district)

    query += " ORDER BY name"

    rows = db.execute(
        query,
        params
    ).fetchall()

    db.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# GET TEACHERS
# ============================================================

@app.route("/api/teachers")
def teachers():

    db = get_db()

    rows = db.execute("""
        SELECT
            t.teacher_id,
            t.first_name,
            t.last_name,
            t.department,
            t.grade_level,
            t.bio,

            s.school_id,
            s.name AS school_name,
            s.district,
            s.city,
            s.state,

            COUNT(r.review_id) AS review_count,

            ROUND(
                AVG(r.rating_overall),
                1
            ) AS rating,

            ROUND(
                AVG(r.rating_difficulty),
                1
            ) AS difficulty,

            ROUND(
                AVG(r.rating_helpfulness),
                1
            ) AS helpfulness

        FROM teachers t

        JOIN schools s
            ON t.school_id = s.school_id

        LEFT JOIN reviews r
            ON t.teacher_id = r.teacher_id
            AND r.status = 'approved'

        GROUP BY
            t.teacher_id

        ORDER BY
            t.last_name,
            t.first_name
    """).fetchall()

    db.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# SEARCH + FILTER TEACHERS
# ============================================================

@app.route("/api/search")
def search():

    search_text = request.args.get(
        "q",
        ""
    ).strip()

    state = request.args.get(
        "state",
        ""
    ).strip()

    district = request.args.get(
        "district",
        ""
    ).strip()

    school_id = request.args.get(
        "school_id",
        ""
    ).strip()

    grade = request.args.get(
        "grade",
        ""
    ).strip()

    subject = request.args.get(
        "subject",
        ""
    ).strip()

    sort = request.args.get(
        "sort",
        "name"
    ).strip()

    db = get_db()

    query = """
        SELECT
            t.teacher_id,
            t.first_name,
            t.last_name,
            t.department,
            t.grade_level,
            t.bio,

            s.school_id,
            s.name AS school_name,
            s.district,
            s.city,
            s.state,

            COUNT(r.review_id) AS review_count,

            ROUND(
                AVG(r.rating_overall),
                1
            ) AS rating,

            ROUND(
                AVG(r.rating_difficulty),
                1
            ) AS difficulty,

            ROUND(
                AVG(r.rating_helpfulness),
                1
            ) AS helpfulness

        FROM teachers t

        JOIN schools s
            ON t.school_id = s.school_id

        LEFT JOIN reviews r
            ON t.teacher_id = r.teacher_id
            AND r.status = 'approved'

        WHERE 1 = 1
    """

    params = []

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search_text:

        search_value = f"%{search_text}%"

        query += """
            AND (
                t.first_name LIKE ?
                OR t.last_name LIKE ?
                OR (t.first_name || ' ' || t.last_name) LIKE ?
                OR t.department LIKE ?
                OR t.grade_level LIKE ?
                OR t.bio LIKE ?
                OR s.name LIKE ?
                OR s.district LIKE ?
                OR s.city LIKE ?
                OR s.state LIKE ?
            )
        """

        params.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value,
            search_value
        ])

    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    if state:

        query += """
            AND s.state = ?
        """

        params.append(state)

    # --------------------------------------------------------
    # DISTRICT
    # --------------------------------------------------------

    if district:

        query += """
            AND s.district = ?
        """

        params.append(district)

    # --------------------------------------------------------
    # SCHOOL
    # --------------------------------------------------------

    if school_id:

        query += """
            AND s.school_id = ?
        """

        params.append(school_id)

    # --------------------------------------------------------
    # GRADE
    # --------------------------------------------------------

    if grade:

        query += """
            AND t.grade_level LIKE ?
        """

        params.append(
            f"%{grade}%"
        )

    # --------------------------------------------------------
    # SUBJECT
    # --------------------------------------------------------

    if subject:

        query += """
            AND t.department LIKE ?
        """

        params.append(
            f"%{subject}%"
        )

    # --------------------------------------------------------
    # GROUP
    # --------------------------------------------------------

    query += """
        GROUP BY t.teacher_id
    """

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    if sort == "highest":

        query += """
            ORDER BY
                CASE
                    WHEN rating IS NULL THEN 1
                    ELSE 0
                END,
                rating DESC,
                t.last_name
        """

    elif sort == "lowest":

        query += """
            ORDER BY
                CASE
                    WHEN rating IS NULL THEN 1
                    ELSE 0
                END,
                rating ASC,
                t.last_name
        """

    elif sort == "reviews":

        query += """
            ORDER BY
                review_count DESC,
                t.last_name
        """

    else:

        query += """
            ORDER BY
                t.last_name,
                t.first_name
        """

    rows = db.execute(
        query,
        params
    ).fetchall()

    db.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# ONE TEACHER
# ============================================================

@app.route("/api/teachers/<int:teacher_id>")
def one_teacher(teacher_id):

    db = get_db()

    row = db.execute("""
        SELECT
            t.teacher_id,
            t.first_name,
            t.last_name,
            t.department,
            t.grade_level,
            t.bio,

            s.school_id,
            s.name AS school_name,
            s.district,
            s.city,
            s.state,

            COUNT(r.review_id) AS review_count,

            ROUND(
                AVG(r.rating_overall),
                1
            ) AS rating,

            ROUND(
                AVG(r.rating_difficulty),
                1
            ) AS difficulty,

            ROUND(
                AVG(r.rating_helpfulness),
                1
            ) AS helpfulness

        FROM teachers t

        JOIN schools s
            ON t.school_id = s.school_id

        LEFT JOIN reviews r
            ON t.teacher_id = r.teacher_id
            AND r.status = 'approved'

        WHERE t.teacher_id = ?

        GROUP BY
            t.teacher_id
    """, (teacher_id,)).fetchone()

    if row is None:
        db.close()
        return jsonify({
            "error": "Teacher not found"
        }), 404

    teacher = dict(row)

    # Get this teacher's approved reviews so teacher.html can display them.
    reviews = db.execute("""
        SELECT
            r.review_id,
            r.teacher_id,
            r.course_name,
            r.reviewer_role,
            r.student_grade_level,
            r.rating_overall,
            r.rating_difficulty,
            r.rating_helpfulness,
            r.review_text,
            r.created_at
        FROM reviews r
        WHERE r.teacher_id = ?
          AND r.status = 'approved'
        ORDER BY r.created_at DESC
    """, (teacher_id,)).fetchall()

    teacher["reviews"] = [dict(review) for review in reviews]

    db.close()

    return jsonify(teacher)


# ============================================================
# REVIEWS
# ============================================================

@app.route("/api/teachers/<int:teacher_id>/reviews", methods=["GET"])
def get_reviews(teacher_id):
    """Return all approved reviews for one teacher."""
    db = get_db()

    teacher_exists = db.execute(
        "SELECT teacher_id FROM teachers WHERE teacher_id = ?",
        (teacher_id,)
    ).fetchone()

    if teacher_exists is None:
        db.close()
        return jsonify({"success": False, "error": "Teacher not found"}), 404

    rows = db.execute("""
        SELECT
            review_id,
            teacher_id,
            course_name,
            reviewer_role,
            student_grade_level,
            rating_overall,
            rating_difficulty,
            rating_helpfulness,
            review_text,
            created_at
        FROM reviews
        WHERE teacher_id = ?
          AND status = 'approved'
        ORDER BY created_at DESC
    """, (teacher_id,)).fetchall()

    db.close()

    reviews = [dict(row) for row in rows]
    return jsonify({
        "success": True,
        "teacher_id": teacher_id,
        "count": len(reviews),
        "reviews": reviews
    })


@app.route("/api/teachers/<int:teacher_id>/reviews", methods=["POST"])
def submit_review(teacher_id):
    """Save an anonymous review using the same review fields as the team's review backend."""
    data = request.get_json(silent=True) if request.is_json else request.form
    data = data or {}

    rating_overall = data.get("rating_overall")
    rating_difficulty = data.get("rating_difficulty")
    rating_helpfulness = data.get("rating_helpfulness")
    review_text = data.get("review_text")
    course_name = data.get("course_name")
    reviewer_role = data.get("reviewer_role", "student")
    student_grade_level = data.get("student_grade_level")

    try:
        rating_overall = int(rating_overall)
        rating_difficulty = int(rating_difficulty)
        rating_helpfulness = int(rating_helpfulness)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Ratings must be numbers from 1 to 5."}), 400

    if not all(1 <= value <= 5 for value in (rating_overall, rating_difficulty, rating_helpfulness)):
        return jsonify({"success": False, "error": "Ratings must be between 1 and 5."}), 400

    if not review_text or len(str(review_text).strip()) < 5:
        return jsonify({"success": False, "error": "Please write at least a few words for your review."}), 400

    db = get_db()

    teacher_exists = db.execute(
        "SELECT teacher_id FROM teachers WHERE teacher_id = ?",
        (teacher_id,)
    ).fetchone()

    if teacher_exists is None:
        db.close()
        return jsonify({"success": False, "error": "Teacher not found"}), 404

    client_hash = get_client_hash()

    try:
        db.execute("""
            INSERT INTO reviews (
                teacher_id, course_name, reviewer_role, student_grade_level,
                rating_overall, rating_difficulty, rating_helpfulness,
                review_text, status, client_fingerprint_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'approved', ?)
        """, (
            teacher_id,
            str(course_name).strip() if course_name else None,
            reviewer_role or "student",
            int(student_grade_level) if student_grade_level else None,
            rating_overall,
            rating_difficulty,
            rating_helpfulness,
            str(review_text).strip(),
            client_hash
        ))

        review_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
        db.commit()

        return jsonify({
            "success": True,
            "message": "Thank you! Your anonymous review has been posted.",
            "review_id": review_id
        }), 201

    except sqlite3.IntegrityError:
        db.rollback()
        return jsonify({
            "success": False,
            "error": "You have already submitted a review for this teacher and course."
        }), 400
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": f"Failed to save review: {str(e)}"}), 500
    finally:
        db.close()


# ============================================================
# TEST DATABASE
# ============================================================

@app.route("/api/test")
def test_database():

    db = get_db()

    schools_count = db.execute(
        "SELECT COUNT(*) FROM schools"
    ).fetchone()[0]

    teachers_count = db.execute(
        "SELECT COUNT(*) FROM teachers"
    ).fetchone()[0]

    reviews_count = db.execute(
        "SELECT COUNT(*) FROM reviews"
    ).fetchone()[0]

    db.close()

    return jsonify({
        "database": "connected",
        "schools": schools_count,
        "teachers": teachers_count,
        "reviews": reviews_count
    })


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )