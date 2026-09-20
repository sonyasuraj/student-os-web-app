-- Enforce foreign key constraints
PRAGMA foreign_keys = ON;

-- Drop tables in dependency order for clean recreation
DROP TABLE IF EXISTS review_responses;
DROP TABLE IF EXISTS review_votes;
DROP TABLE IF EXISTS review_tags;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS moderation_reports;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS schools;

-- =========================================================================
-- 1. SCHOOLS TABLE
-- Directory of schools.
-- =========================================================================
CREATE TABLE schools (
    school_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    school_level TEXT CHECK(school_level IN ('elementary', 'middle', 'high', 'k-12', 'other')) NOT NULL,
    district TEXT,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================================
-- 2. TEACHERS TABLE
-- Crowdsourced teacher profiles. Anyone can add a teacher.
-- =========================================================================
CREATE TABLE teachers (
    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    department TEXT NOT NULL,       -- e.g., 'Math', 'Science', 'English', '5th Grade'
    grade_level TEXT NOT NULL,      -- e.g., '6-8', '10th Grade'
    bio TEXT,                       -- Optional description or subjects taught
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE
);

-- =========================================================================
-- 3. REVIEWS TABLE (100% Anonymous Submissions)
-- Uses client_fingerprint_hash to throttle review spam.
-- =========================================================================
CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    course_name TEXT,               -- e.g., 'Algebra 1', 'AP Biology'
    reviewer_role TEXT CHECK(reviewer_role IN ('student', 'parent', 'alumni', 'other')) DEFAULT 'student',
    student_grade_level INTEGER CHECK(student_grade_level BETWEEN 1 AND 12),
    rating_overall INTEGER CHECK(rating_overall BETWEEN 1 AND 5) NOT NULL,
    rating_difficulty INTEGER CHECK(rating_difficulty BETWEEN 1 AND 5) NOT NULL,
    rating_helpfulness INTEGER CHECK(rating_helpfulness BETWEEN 1 AND 5) NOT NULL,
    review_text TEXT NOT NULL,
    status TEXT CHECK(status IN ('pending', 'approved', 'rejected', 'flagged')) DEFAULT 'approved',
    client_fingerprint_hash TEXT NOT NULL, -- Anonymous identifier to prevent spam
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    UNIQUE(teacher_id, course_name, client_fingerprint_hash)
);

-- =========================================================================
-- 4. TAGS LOOKUP TABLE
-- Predefined descriptors (e.g., 'Gives Good Feedback', 'Tough Grader').
-- =========================================================================
CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT UNIQUE NOT NULL
);

-- =========================================================================
-- 5. REVIEW_TAGS JUNCTION TABLE
-- Many-to-Many mapping between Reviews and Tags.
-- =========================================================================
CREATE TABLE review_tags (
    review_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (review_id, tag_id),
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);

-- =========================================================================
-- 6. REVIEW_VOTES TABLE (Anonymous Likes & Dislikes)
-- Tracks votes using the client hash so users can see their liked/disliked
-- status and cannot vote more than once per review.
-- =========================================================================
CREATE TABLE review_votes (
    vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    client_fingerprint_hash TEXT NOT NULL,
    vote_value INTEGER CHECK(vote_value IN (-1, 1)) NOT NULL, -- 1 = Like, -1 = Dislike
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE,
    UNIQUE(review_id, client_fingerprint_hash)
);

-- =========================================================================
-- 7. REVIEW_RESPONSES TABLE (Anonymous Responses / Discussions)
-- Anyone (teacher, student, or community member) can post a response.
-- An optional 'responder_label' lets them state who they are (e.g. 'Teacher', 'Student').
-- =========================================================================
CREATE TABLE review_responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    responder_label TEXT DEFAULT 'Anonymous', -- e.g., 'Teacher', 'Fellow Student', 'Parent'
    response_text TEXT NOT NULL,
    client_fingerprint_hash TEXT NOT NULL,   -- Prevents spamming responses
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE
);

-- =========================================================================
-- 8. MODERATION_REPORTS TABLE
-- Anonymous flagging of inappropriate content.
-- =========================================================================
CREATE TABLE moderation_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    reason TEXT CHECK(reason IN ('bullying', 'inappropriate_language', 'false_information', 'other')) NOT NULL,
    notes TEXT,
    reporter_fingerprint_hash TEXT,
    resolved INTEGER CHECK(resolved IN (0, 1)) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE
);

-- =========================================================================
-- PERFORMANCE INDEXES
-- =========================================================================
CREATE INDEX idx_teachers_school ON teachers(school_id);
CREATE INDEX idx_teachers_name ON teachers(last_name, first_name);
CREATE INDEX idx_reviews_teacher ON reviews(teacher_id);
CREATE INDEX idx_reviews_status ON reviews(status);
CREATE INDEX idx_reviews_fingerprint ON reviews(client_fingerprint_hash);
CREATE INDEX idx_votes_fingerprint ON review_votes(client_fingerprint_hash);
CREATE INDEX idx_responses_review ON review_responses(review_id);

-- =========================================================================
-- SEED DATA (For Immediate Testing)
-- =========================================================================
INSERT INTO schools (school_id, name, school_level, city, state) VALUES 
(1, 'Oak Creek Middle School', 'middle', 'Los Angeles', 'CA');

INSERT INTO teachers (school_id, first_name, last_name, department, grade_level, bio) VALUES 
(1, 'Sarah', 'Connor', 'Science', '7-8', '7th and 8th Grade Physical & Life Sciences'),
(1, 'David', 'Miller', 'Mathematics', '6-7', 'Middle School Pre-Algebra and Algebra 1');

INSERT INTO tags (tag_name) VALUES 
('Gives Good Feedback'),
('Tough Grader'),
('Lots of Homework'),
('Inspirational'),
('Fun Projects'),
('Clear Grading Criteria');
