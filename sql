-- ============================================================
-- RIO NORTE JUNIOR HIGH SCHOOL
-- RATE MY TEACHER DATABASE
-- SQLite
-- ============================================================

PRAGMA foreign_keys = ON;


-- ============================================================
-- DELETE OLD TABLES
-- ============================================================

DROP TABLE IF EXISTS review_responses;
DROP TABLE IF EXISTS review_votes;
DROP TABLE IF EXISTS review_tags;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS moderation_reports;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS schools;


-- ============================================================
-- SCHOOLS
-- ============================================================

CREATE TABLE schools (
    school_id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    school_level TEXT
        CHECK (
            school_level IN (
                'elementary',
                'middle',
                'high',
                'k-12',
                'other'
            )
        )
        NOT NULL,

    district TEXT,

    city TEXT NOT NULL,

    state TEXT NOT NULL,

    zip_code TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- TEACHERS
-- ============================================================

CREATE TABLE teachers (
    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,

    school_id INTEGER NOT NULL,

    first_name TEXT NOT NULL,

    last_name TEXT NOT NULL,

    department TEXT NOT NULL,

    grade_level TEXT NOT NULL,

    bio TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (school_id)
        REFERENCES schools(school_id)
        ON DELETE CASCADE
);


-- ============================================================
-- REVIEWS
-- ============================================================

CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,

    teacher_id INTEGER NOT NULL,

    course_name TEXT,

    reviewer_role TEXT
        CHECK (
            reviewer_role IN (
                'student',
                'parent',
                'alumni',
                'other'
            )
        )
        DEFAULT 'student',

    student_grade_level INTEGER
        CHECK (
            student_grade_level BETWEEN 1 AND 12
        ),

    rating_overall INTEGER
        CHECK (
            rating_overall BETWEEN 1 AND 5
        )
        NOT NULL,

    rating_difficulty INTEGER
        CHECK (
            rating_difficulty BETWEEN 1 AND 5
        )
        NOT NULL,

    rating_helpfulness INTEGER
        CHECK (
            rating_helpfulness BETWEEN 1 AND 5
        )
        NOT NULL,

    review_text TEXT NOT NULL,

    status TEXT
        CHECK (
            status IN (
                'pending',
                'approved',
                'rejected',
                'flagged'
            )
        )
        DEFAULT 'pending',

    client_fingerprint_hash TEXT NOT NULL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (teacher_id)
        REFERENCES teachers(teacher_id)
        ON DELETE CASCADE,

    UNIQUE (
        teacher_id,
        course_name,
        client_fingerprint_hash
    )
);


-- ============================================================
-- TAGS
-- ============================================================

CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,

    tag_name TEXT UNIQUE NOT NULL
);


-- ============================================================
-- REVIEW ↔ TAGS
-- ============================================================

CREATE TABLE review_tags (
    review_id INTEGER NOT NULL,

    tag_id INTEGER NOT NULL,

    PRIMARY KEY (
        review_id,
        tag_id
    ),

    FOREIGN KEY (review_id)
        REFERENCES reviews(review_id)
        ON DELETE CASCADE,

    FOREIGN KEY (tag_id)
        REFERENCES tags(tag_id)
        ON DELETE CASCADE
);


-- ============================================================
-- REVIEW VOTES
-- ============================================================

CREATE TABLE review_votes (
    vote_id INTEGER PRIMARY KEY AUTOINCREMENT,

    review_id INTEGER NOT NULL,

    client_fingerprint_hash TEXT NOT NULL,

    vote_value INTEGER
        CHECK (
            vote_value IN (-1, 1)
        )
        NOT NULL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (review_id)
        REFERENCES reviews(review_id)
        ON DELETE CASCADE,

    UNIQUE (
        review_id,
        client_fingerprint_hash
    )
);


-- ============================================================
-- REVIEW RESPONSES
-- ============================================================

CREATE TABLE review_responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,

    review_id INTEGER NOT NULL,

    responder_label TEXT
        DEFAULT 'Anonymous',

    response_text TEXT NOT NULL,

    client_fingerprint_hash TEXT NOT NULL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (review_id)
        REFERENCES reviews(review_id)
        ON DELETE CASCADE
);


-- ============================================================
-- MODERATION REPORTS
-- ============================================================

CREATE TABLE moderation_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,

    review_id INTEGER NOT NULL,

    reason TEXT
        CHECK (
            reason IN (
                'bullying',
                'inappropriate_language',
                'false_information',
                'other'
            )
        )
        NOT NULL,

    notes TEXT,

    reporter_fingerprint_hash TEXT,

    resolved INTEGER
        CHECK (
            resolved IN (0, 1)
        )
        DEFAULT 0,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (review_id)
        REFERENCES reviews(review_id)
        ON DELETE CASCADE
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_teachers_school
ON teachers(school_id);

CREATE INDEX idx_teachers_name
ON teachers(last_name, first_name);

CREATE INDEX idx_reviews_teacher
ON reviews(teacher_id);

CREATE INDEX idx_reviews_status
ON reviews(status);

CREATE INDEX idx_reviews_fingerprint
ON reviews(client_fingerprint_hash);

CREATE INDEX idx_votes_fingerprint
ON review_votes(client_fingerprint_hash);

CREATE INDEX idx_responses_review
ON review_responses(review_id);


-- ============================================================
-- SCHOOL
-- ============================================================

INSERT INTO schools (
    school_id,
    name,
    school_level,
    district,
    city,
    state
)
VALUES (
    1,
    'Rio Norte Junior High School',
    'middle',
    'William S. Hart Union High School District',
    'Santa Clarita',
    'CA'
);


-- ============================================================
-- TEACHERS
-- ============================================================

INSERT INTO teachers (
    school_id,
    first_name,
    last_name,
    department,
    grade_level,
    bio
)
VALUES

-- ============================================================
-- ENGLISH
-- ============================================================

(
    1,
    'Christopher',
    'Bangasser',
    'English',
    'GRADE 8',
    NULL
),

(
    1,
    'Tiffany',
    'Cabrera',
    'English',
    'YELLOWSTONE * GRADE 7',
    NULL
),

(
    1,
    'Elena',
    'Davis',
    'English',
    'GRADE 8',
    NULL
),

(
    1,
    'Ramona',
    'Schantz',
    'English',
    'TAMBO * GRADE 7',
    NULL
),

(
    1,
    'Julie',
    'Schneider',
    'English',
    'YELLOWSTONE * GRADE 7',
    NULL
),

(
    1,
    'Kristen',
    'Sifferman',
    'English',
    'GRADE 8',
    NULL
),

(
    1,
    'Lisa',
    'Simmons',
    'English',
    'TAMBO * GRADE 7',
    NULL
),

(
    1,
    'Athanasia',
    'Smith',
    'English and History',
    'GRADE 8',
    NULL
),


-- ============================================================
-- MATHEMATICS
-- ============================================================

(
    1,
    'Karen',
    'Choi',
    'Mathematics',
    'GRADE 8',
    NULL
),

(
    1,
    'Lesley',
    'Day',
    'Mathematics',
    'GRADE 7',
    NULL
),

(
    1,
    'Anna',
    'Fajardo',
    'Mathematics',
    'GRADE 8',
    NULL
),

(
    1,
    'Kim',
    'Grandbois',
    'Math 8 and Algebra 1',
    'GRADE 8',
    NULL
),

(
    1,
    'Laura',
    'Groller',
    'Math 7',
    'GRADE 7',
    NULL
),

(
    1,
    'Kim',
    'Joyce',
    'Math 8 and Algebra 1',
    'GRADE 8',
    NULL
),

(
    1,
    'Mitzi',
    'Mandel',
    'Mathematics',
    'GRADE 8',
    NULL
),

(
    1,
    'Alicia',
    'Rippe',
    'Math and Algebra 1',
    'GRADE 8',
    NULL
),

(
    1,
    'Kirsten',
    'Shaw',
    'Math 7 AM7',
    'TAMBO * GRADE 7',
    NULL
),

(
    1,
    'Lisa',
    'Van Dyke',
    'Science and AM7',
    'TAMBO * GRADE 7',
    NULL
),


-- ============================================================
-- HISTORY
-- ============================================================

(
    1,
    'Janelle',
    'Burkholder',
    'History Teacher',
    'Tyger * GRADE 7',
    NULL
),

(
    1,
    'Skylar',
    'Hogan',
    'History Teacher',
    'GRADE 8',
    NULL
),

(
    1,
    'Ron',
    'Ippolito',
    'History Teacher, Rio TV Advisor',
    'GRADE 8',
    NULL
),

(
    1,
    'Bradley',
    'Knutsen',
    'History Teacher, Department Chair, ASB',
    'GRADE 8',
    NULL
),

(
    1,
    'Jeanette',
    'Kratofil',
    'History Teacher',
    'Tambo * GRADE 7',
    NULL
),

(
    1,
    'Jerry',
    'Malkowski',
    'History Teacher',
    'GRADE 8',
    NULL
),

(
    1,
    'Jennifer',
    'Pulaski',
    'History Teacher',
    'GRADE 7 * Yellowstone',
    NULL
),

(
    1,
    'Matthew',
    'Sheridan',
    'History Teacher',
    'GRADE 8?',
    NULL
),


-- ============================================================
-- SPECIAL EDUCATION
-- ============================================================

(
    1,
    'Shalen',
    'Burwell (Casini)',
    'Special Education Teacher',
    '',
    NULL
),

(
    1,
    'Heather',
    'Cruz',
    'Special Education Teacher',
    '',
    NULL
),

(
    1,
    'Asha',
    'Kakonde',
    'Special Education Teacher',
    '',
    NULL
),


-- ============================================================
-- PHYSICAL EDUCATION
-- ============================================================

(
    1,
    'Aaron',
    'Burleson',
    'Physical Education',
    'NA',
    NULL
),

(
    1,
    'Carrie',
    'Carrizales',
    'Physical Education',
    'NA',
    NULL
),

(
    1,
    'Dawn',
    'Cooper',
    'Physical Education',
    'NA',
    NULL
),

(
    1,
    'Darryl',
    'Stroh',
    'Physical Education',
    'NA',
    NULL
),

(
    1,
    'Angela',
    'Welch',
    'Physical Education',
    'NA',
    NULL
),


-- ============================================================
-- SCIENCE
-- ============================================================

(
    1,
    'Jenny',
    'Bretthauer',
    'Science',
    'GRADE 7 * Tyger',
    NULL
),

(
    1,
    'Eduardo',
    'Cedeño',
    'Science',
    'GRADE 8',
    NULL
),

(
    1,
    'Lisa',
    'James',
    'Science',
    'GRADE 7 * Tambo',
    NULL
),

(
    1,
    'Stephanie',
    'Madrid',
    'Science',
    'GRADE 8',
    NULL
),

(
    1,
    'Samantha',
    'Malcolm',
    'Science',
    'GRADE 7 * Yellowstone',
    NULL
),

(
    1,
    'Jase',
    'St Peter',
    'Science',
    'GRADE 8',
    NULL
),

(
    1,
    'Diane',
    'Untalan',
    'Science',
    'GRADE 8',
    NULL
);


-- ============================================================
-- REVIEW TAGS
-- ============================================================

INSERT INTO tags (tag_name)
VALUES
('Gives Good Feedback'),
('Tough Grader'),
('Lots of Homework'),
('Inspirational'),
('Fun Projects'),
('Clear Grading Criteria'),
('Helpful'),
('Clear Explanations'),
('Respectful'),
('Engaging');


-- ============================================================
-- DONE
-- ============================================================