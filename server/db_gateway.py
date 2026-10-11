"""
Database Gateway for Rate My Teacher
Handles all SQLite queries, transactions, and aggregate calculations.
"""

import os
import sqlite3

# Locate app_database.db in the database/ directory relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rmt.db")


def get_db():
    """Establishes database connection with Row factory and Foreign Keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ---------------------------------------------------------------------------
# SCHOOL QUERIES
# ---------------------------------------------------------------------------

def get_all_schools():
    """Returns all schools for dropdown selectors."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM schools ORDER BY name ASC")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# TEACHER QUERIES
# ---------------------------------------------------------------------------

def get_all_teachers(search_query=None, department=None, grade_level=None):
    """
    Retrieves teachers with joined school info and computed review summary stats:
    - total_reviews
    - avg_overall (rounded to 1 decimal)
    - avg_difficulty (rounded to 1 decimal)
    """
    conn = get_db()
    cur = conn.cursor()

    sql = """
        SELECT 
            t.teacher_id,
            t.school_id,
            t.first_name,
            t.last_name,
            t.department,
            t.grade_level,
            t.bio,
            t.created_at,
            s.name AS school_name,
            s.city AS school_city,
            s.state AS school_state,
            COUNT(r.review_id) AS total_reviews,
            ROUND(AVG(r.rating_overall), 1) AS avg_overall,
            ROUND(AVG(r.rating_difficulty), 1) AS avg_difficulty,
            ROUND(AVG(r.rating_helpfulness), 1) AS avg_helpfulness
        FROM teachers t
        JOIN schools s ON t.school_id = s.school_id
        LEFT JOIN reviews r ON t.teacher_id = r.teacher_id AND r.status = 'approved'
        WHERE 1=1
    """
    params = []

    if search_query:
        query_wildcard = f"%{search_query.strip()}%"
        sql += """ AND (
            t.first_name LIKE ? OR 
            t.last_name LIKE ? OR 
            t.department LIKE ? OR 
            s.name LIKE ?
        )"""
        params.extend([query_wildcard, query_wildcard, query_wildcard, query_wildcard])

    if department:
        sql += " AND t.department = ?"
        params.append(department.strip())

    if grade_level:
        sql += " AND t.grade_level LIKE ?"
        params.append(f"%{grade_level.strip()}%")

    sql += """
        GROUP BY t.teacher_id
        ORDER BY t.last_name ASC, t.first_name ASC
    """

    cur.execute(sql, params)
    teachers = [dict(row) for row in cur.fetchall()]
    conn.close()
    return teachers


def get_teacher_by_id(teacher_id):
    """Returns detailed profile and aggregate scores for a specific teacher."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            t.teacher_id,
            t.school_id,
            t.first_name,
            t.last_name,
            t.department,
            t.grade_level,
            t.bio,
            t.created_at,
            s.name AS school_name,
            s.city AS school_city,
            s.state AS school_state,
            COUNT(r.review_id) AS total_reviews,
            COALESCE(ROUND(AVG(r.rating_overall), 1), 0.0) AS avg_overall,
            COALESCE(ROUND(AVG(r.rating_difficulty), 1), 0.0) AS avg_difficulty,
            COALESCE(ROUND(AVG(r.rating_helpfulness), 1), 0.0) AS avg_helpfulness
        FROM teachers t
        JOIN schools s ON t.school_id = s.school_id
        LEFT JOIN reviews r ON t.teacher_id = r.teacher_id AND r.status = 'approved'
        WHERE t.teacher_id = ?
        GROUP BY t.teacher_id
    """, (teacher_id,))
    row = cur.fetchone()
    teacher = dict(row) if row else None
    conn.close()
    return teacher


def add_teacher(school_id, first_name, last_name, department, grade_level, bio=""):
    """
    Inserts a new teacher into the teachers table.
    Returns (success: bool, teacher_id: int or None, error: str or None).
    """
    if not school_id or not first_name or not last_name or not department or not grade_level:
        return False, None, "All fields (School, First Name, Last Name, Department, Grade Level) are required."

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO teachers (school_id, first_name, last_name, department, grade_level, bio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            int(school_id),
            first_name.strip(),
            last_name.strip(),
            department.strip(),
            grade_level.strip(),
            (bio or "").strip()
        ))
        teacher_id = cur.lastrowid
        conn.commit()
        return True, teacher_id, None
    except sqlite3.IntegrityError as e:
        return False, None, f"Database integrity error: {str(e)}"
    except Exception as e:
        return False, None, f"Failed to add teacher: {str(e)}"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# REVIEW QUERIES
# ---------------------------------------------------------------------------

def get_teacher_reviews(teacher_id, current_client_hash=None):
    """
    Retrieves all approved reviews for a teacher, including attached tags,
    helpful vote counts, and user's previous vote status.
    """
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
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
            r.created_at,
            COALESCE(SUM(CASE WHEN v.vote_value = 1 THEN 1 ELSE 0 END), 0) AS upvotes,
            COALESCE(SUM(CASE WHEN v.vote_value = -1 THEN 1 ELSE 0 END), 0) AS downvotes,
            MAX(CASE WHEN v.client_fingerprint_hash = ? THEN v.vote_value ELSE 0 END) AS user_vote
        FROM reviews r
        LEFT JOIN review_votes v ON r.review_id = v.review_id
        WHERE r.teacher_id = ? AND r.status = 'approved'
        GROUP BY r.review_id
        ORDER BY r.created_at DESC
    """, (current_client_hash or "", teacher_id))

    reviews = [dict(row) for row in cur.fetchall()]

    # Fetch tags for each review
    for rev in reviews:
        cur.execute("""
            SELECT t.tag_id, t.tag_name
            FROM tags t
            JOIN review_tags rt ON t.tag_id = rt.tag_id
            WHERE rt.review_id = ?
            ORDER BY t.tag_name ASC
        """, (rev["review_id"],))
        rev["tags"] = [dict(t) for t in cur.fetchall()]

    conn.close()
    return reviews


def add_review(teacher_id, rating_overall, rating_difficulty, rating_helpfulness,
               review_text, client_fingerprint_hash, course_name=None,
               reviewer_role="student", student_grade_level=None, tag_ids=None):
    """
    Saves a new review.
    Enforces 100% anonymous rate-limiting: one review per (teacher, course, client_fingerprint_hash).
    Returns (success: bool, review_id: int or None, error: str or None).
    """
    # Validation
    if not teacher_id:
        return False, None, "Teacher ID is missing."
    if not (1 <= int(rating_overall) <= 5):
        return False, None, "Overall rating must be between 1 and 5."
    if not (1 <= int(rating_difficulty) <= 5):
        return False, None, "Difficulty rating must be between 1 and 5."
    if not (1 <= int(rating_helpfulness) <= 5):
        return False, None, "Helpfulness rating must be between 1 and 5."
    if not review_text or len(review_text.strip()) < 5:
        return False, None, "Please write at least a few words for your review comments."

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO reviews (
                teacher_id, course_name, reviewer_role, student_grade_level,
                rating_overall, rating_difficulty, rating_helpfulness,
                review_text, status, client_fingerprint_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'approved', ?)
        """, (
            int(teacher_id),
            (course_name or "").strip() or None,
            reviewer_role,
            int(student_grade_level) if student_grade_level else None,
            int(rating_overall),
            int(rating_difficulty),
            int(rating_helpfulness),
            review_text.strip(),
            client_fingerprint_hash
        ))
        review_id = cur.lastrowid

        # Insert selected tags
        if tag_ids and isinstance(tag_ids, list):
            for t_id in tag_ids:
                cur.execute("""
                    INSERT OR IGNORE INTO review_tags (review_id, tag_id)
                    VALUES (?, ?)
                """, (review_id, int(t_id)))

        conn.commit()
        return True, review_id, None

    except sqlite3.IntegrityError:
        return False, None, "You have already submitted a review for this teacher and course."
    except Exception as e:
        return False, None, f"Failed to save review: {str(e)}"
    finally:
        conn.close()


def get_all_tags():
    """Returns all pre-seeded review tags (e.g. Fun Projects, Tough Grader)."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tags ORDER BY tag_name ASC")
    tags = [dict(row) for row in cur.fetchall()]
    conn.close()
    return tags
