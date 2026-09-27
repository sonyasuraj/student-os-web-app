

from flask import Flask, jsonify, request, send_from_directory
import sqlite3
import os

app = Flask(__name__)

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
    return db


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

    db.close()

    if row is None:
        return jsonify({
            "error": "Teacher not found"
        }), 404

    return jsonify(dict(row))


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