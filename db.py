import sqlite3

DB_PATH = "app_database.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# 1. Create a Teacher
def add_teacher(school_id, first_name, last_name, department, grade_level, bio=""):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO teachers (school_id, first_name, last_name, department, grade_level, bio)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (school_id, first_name.strip(), last_name.strip(), department.strip(), grade_level.strip(), bio.strip()))
    teacher_id = cur.lastrowid
    conn.commit()
    conn.close()
    return teacher_id

# 2. Add an Anonymous Response to a Review
def add_review_response(review_id, response_text, client_hash, responder_label="Anonymous"):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO review_responses (review_id, responder_label, response_text, client_fingerprint_hash)
        VALUES (?, ?, ?, ?)
    """, (review_id, responder_label, response_text.strip(), client_hash))
    response_id = cur.lastrowid
    conn.commit()
    conn.close()
    return response_id

# 3. Fetch Reviews along with Responses and Current User's Vote
def get_teacher_reviews(teacher_id, current_client_hash):
    conn = get_db()
    cur = conn.cursor()
    
    # Get reviews with current user's vote status
    cur.execute("""
        SELECT 
            r.*,
            COALESCE(v.vote_value, 0) AS user_vote
        FROM reviews r
        LEFT JOIN review_votes v 
            ON r.review_id = v.review_id AND v.client_fingerprint_hash = ?
        WHERE r.teacher_id = ? AND r.status = 'approved'
        ORDER BY r.created_at DESC
    """, (current_client_hash, teacher_id))
    reviews = [dict(row) for row in cur.fetchall()]
    
    # Attach responses to each review
    for rev in reviews:
        cur.execute("""
            SELECT response_id, responder_label, response_text, created_at
            FROM review_responses
            WHERE review_id = ?
            ORDER BY created_at ASC
        """, (rev["review_id"],))
        rev["responses"] = [dict(row) for row in cur.fetchall()]
        
    conn.close()
    return reviews
