-- Ensure SQLite strictly enforces foreign key constraints
PRAGMA foreign_keys = ON;

-- Drop tables if they exist (useful for testing/resetting the database)
DROP TABLE IF EXISTS review_responses;
DROP TABLE IF EXISTS review_votes;
DROP TABLE IF EXISTS review_tags;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS moderation_reports;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS teachers;
DROP TABLE IF EXISTS schools;
DROP TABLE IF EXISTS password_resets;

-- =========================================================================
-- 1. SCHOOLS TABLE
-- Parent of both Teachers and Users.
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
-- Belongs to a School (Many-to-One).
-- =========================================================================
CREATE TABLE teachers (
    teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    department TEXT, -- e.g., 'Math', 'Science', '5th Grade'
    grade_level TEXT, -- e.g., '6-8', '10'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE CASCADE
);

-- =========================================================================
-- 3. USERS TABLE
-- Can optionally belong to a School.
-- Designed with minimal PII (COPPA compliant). No real names or emails.
-- =========================================================================
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    school_id INTEGER,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL, -- Required for login & password reset
    password_hash TEXT NOT NULL,
    grade_level INTEGER CHECK(grade_level BETWEEN 1 AND 12), -- Optional for teachers
    role TEXT CHECK(role IN ('student', 'teacher', 'moderator', 'admin')) DEFAULT 'student',
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(school_id) ON DELETE SET NULL
);

-- =========================================================================
-- 4. REVIEWS TABLE
-- The core transactional table.
-- Links a User (Author) to a Teacher (Subject).
-- =========================================================================
CREATE TABLE reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    course_name TEXT, -- e.g., 'AP Biology', 'Algebra 1'
    rating_overall INTEGER CHECK(rating_overall BETWEEN 1 AND 5) NOT NULL,
    rating_difficulty INTEGER CHECK(rating_difficulty BETWEEN 1 AND 5) NOT NULL,
    rating_helpfulness INTEGER CHECK(rating_helpfulness BETWEEN 1 AND 5) NOT NULL,
    review_text TEXT NOT NULL,
    status TEXT CHECK(status IN ('pending', 'approved', 'rejected', 'flagged')) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    -- Prevents a user from spamming multiple reviews for the exact same class/teacher
    UNIQUE(teacher_id, user_id, course_name) 
);

-- =========================================================================
-- 5. TAGS LOOKUP TABLE
-- Predefined descriptors (e.g., "Tough Grader", "Fun Projects").
-- =========================================================================
CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT UNIQUE NOT NULL
);

-- =========================================================================
-- 6. REVIEW_TAGS JUNCTION TABLE
-- Many-to-Many join table linking Reviews to Tags.
-- =========================================================================
CREATE TABLE review_tags (
    review_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (review_id, tag_id),
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);

-- =========================================================================
-- 7. REVIEW_VOTES TABLE
-- Stores Likes/Dislikes on reviews.
-- Links a User to a Review to enforce single-voting.
-- =========================================================================
CREATE TABLE review_votes (
    vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    vote_value INTEGER CHECK(vote_value IN (-1, 1)) NOT NULL, -- 1 = Like (Up), -1 = Dislike (Down)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    -- Enforces that a user can only vote on a specific review once
    UNIQUE(review_id, user_id) 
);

-- =========================================================================
-- 8. REVIEW_RESPONSES TABLE
-- Allows verified accounts/admins to post a single reply/clarification to a review.
-- =========================================================================
CREATE TABLE review_responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER UNIQUE NOT NULL, -- UNIQUE enforces a One-to-One reply limit per review
    responder_user_id INTEGER NOT NULL,
    response_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE,
    FOREIGN KEY (responder_user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- =========================================================================
-- 9. MODERATION_REPORTS TABLE
-- Handles safety/flagging of inappropriate reviews.
-- =========================================================================
CREATE TABLE moderation_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,
    reporter_user_id INTEGER NOT NULL,
    reason TEXT CHECK(reason IN ('bullying', 'inappropriate_language', 'false_information', 'other')) NOT NULL,
    notes TEXT,
    resolved INTEGER CHECK(resolved IN (0, 1)) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) ON DELETE CASCADE,
    FOREIGN KEY (reporter_user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- =========================================================================
-- 10. PASSWORD_RESETS TABLE
-- Tracks password reset tokens.
-- =========================================================================
CREATE TABLE password_resets (
    reset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    expires_at DATETIME NOT NULL,
    used INTEGER CHECK(used IN (0, 1)) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- =========================================================================
-- PERFORMANCE INDEXES
-- Recommended to ensure lookups remain instant as data scales.
-- =========================================================================
CREATE INDEX idx_teachers_school ON teachers(school_id);
CREATE INDEX idx_teachers_name ON teachers(last_name, first_name);
CREATE INDEX idx_reviews_teacher ON reviews(teacher_id);
CREATE INDEX idx_reviews_status ON reviews(status);
