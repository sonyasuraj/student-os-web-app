-- ===========================================================================
-- RATE MY TEACHER — SAMPLE SEED DATA
-- ===========================================================================
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- 1. SCHOOLS
-- ---------------------------------------------------------------------------
INSERT OR IGNORE INTO schools (school_id, name, school_level, district, city, state, zip_code) VALUES
(1, 'Oak Creek Middle School', 'middle', 'Unified School District', 'Los Angeles', 'CA', '90001'),
(2, 'Lincoln High School', 'high', 'Metro Unified District', 'San Francisco', 'CA', '94102'),
(3, 'Pinecrest Elementary School', 'elementary', 'Valley School District', 'Pasadena', 'CA', '91101');

-- ---------------------------------------------------------------------------
-- 2. TEACHERS
-- ---------------------------------------------------------------------------
INSERT OR IGNORE INTO teachers (teacher_id, school_id, first_name, last_name, department, grade_level, bio) VALUES
(1, 1, 'David', 'Miller', 'Mathematics', '6-7', 'Middle school Pre-Algebra & Algebra 1 teacher. Math Olympiad advisor.'),
(2, 1, 'Sarah', 'Connor', 'Science', '7-8', 'Physical & Life Sciences teacher. Robotics Club mentor and science fair coordinator.'),
(3, 1, 'Maria', 'Rodriguez', 'English', '6-8', 'Language Arts, Creative Writing, and School Newspaper advisor.'),
(4, 2, 'Robert', 'Chen', 'History', '9-11', 'AP U.S. History and World Geography teacher. Model UN advisor.'),
(5, 2, 'Emily', 'Watson', 'Art', '9-12', 'Studio Art, Digital Illustration, and Yearbook coordinator.'),
(6, 1, 'Marcus', 'Johnson', 'Physical Education', '6-8', 'PE teacher and Middle School Track & Field head coach.');

-- ---------------------------------------------------------------------------
-- 3. REVIEW TAGS
-- ---------------------------------------------------------------------------
INSERT OR IGNORE INTO tags (tag_id, tag_name) VALUES
(1, 'Gives Good Feedback'),
(2, 'Tough Grader'),
(3, 'Lots of Homework'),
(4, 'Inspirational'),
(5, 'Fun Projects'),
(6, 'Clear Grading Criteria'),
(7, 'Patient & Kind'),
(8, 'Engaging Lectures'),
(9, 'Test Heavy'),
(10, 'Extra Credit Offered');

-- ---------------------------------------------------------------------------
-- 4. SAMPLE REVIEWS
-- ---------------------------------------------------------------------------
-- Teacher 1: Mr. David Miller (Math)
INSERT OR IGNORE INTO reviews (
    review_id, teacher_id, course_name, reviewer_role, student_grade_level,
    rating_overall, rating_difficulty, rating_helpfulness,
    review_text, status, client_fingerprint_hash
) VALUES
(1, 1, 'Pre-Algebra', 'student', 7, 5, 3, 5,
 'Mr. Miller explains equations using pizza slices! His tests are fair if you do the practice problems. Best math teacher ever.',
 'approved', 'anon_hash_student_01'),

(2, 1, 'Algebra 1', 'student', 7, 5, 4, 5,
 'He is always available during lunch for extra tutoring. The homework load is manageable and tests match the study guides.',
 'approved', 'anon_hash_student_02'),

(3, 1, 'Pre-Algebra', 'parent', NULL, 4, 3, 4,
 'My daughter gained so much confidence in math this semester thanks to Mr. Miller''s patient teaching style.',
 'approved', 'anon_hash_parent_01');

-- Teacher 2: Ms. Sarah Connor (Science)
INSERT OR IGNORE INTO reviews (
    review_id, teacher_id, course_name, reviewer_role, student_grade_level,
    rating_overall, rating_difficulty, rating_helpfulness,
    review_text, status, client_fingerprint_hash
) VALUES
(4, 2, '8th Grade Science', 'student', 8, 4, 4, 5,
 'The robotics and rocket projects were incredible! She is a strict grader on lab reports, so make sure to follow the rubric.',
 'approved', 'anon_hash_student_03'),

(5, 2, 'Physical Science', 'student', 8, 5, 4, 5,
 'Inspiring teacher who makes science feel like discovery rather than memorizing a textbook. Tough but very fair.',
 'approved', 'anon_hash_student_04');

-- Teacher 3: Ms. Maria Rodriguez (English)
INSERT OR IGNORE INTO reviews (
    review_id, teacher_id, course_name, reviewer_role, student_grade_level,
    rating_overall, rating_difficulty, rating_helpfulness,
    review_text, status, client_fingerprint_hash
) VALUES
(6, 3, 'Creative Writing', 'student', 7, 5, 2, 5,
 'Loved her book club discussions! She gives very detailed feedback on essays and helps you improve your writing.',
 'approved', 'anon_hash_student_05');

-- Teacher 4: Mr. Robert Chen (History)
INSERT OR IGNORE INTO reviews (
    review_id, teacher_id, course_name, reviewer_role, student_grade_level,
    rating_overall, rating_difficulty, rating_helpfulness,
    review_text, status, client_fingerprint_hash
) VALUES
(7, 4, 'World Geography', 'student', 9, 4, 3, 4,
 'Engaging storyteller. The map quizzes can be tricky, but you will learn a lot about world cultures.',
 'approved', 'anon_hash_student_06');

-- ---------------------------------------------------------------------------
-- 5. ATTACH TAGS TO REVIEWS
-- ---------------------------------------------------------------------------
INSERT OR IGNORE INTO review_tags (review_id, tag_id) VALUES
(1, 5), -- Review 1: Fun Projects
(1, 1), -- Review 1: Gives Good Feedback
(2, 7), -- Review 2: Patient & Kind
(2, 6), -- Review 2: Clear Grading Criteria
(3, 7), -- Review 3: Patient & Kind
(4, 2), -- Review 4: Tough Grader
(4, 5), -- Review 4: Fun Projects
(5, 4), -- Review 5: Inspirational
(5, 8), -- Review 5: Engaging Lectures
(6, 1), -- Review 6: Gives Good Feedback
(6, 4), -- Review 6: Inspirational
(7, 8); -- Review 7: Engaging Lectures

-- ---------------------------------------------------------------------------
-- 6. REVIEW HELPFUL VOTES
-- ---------------------------------------------------------------------------
INSERT OR IGNORE INTO review_votes (review_id, client_fingerprint_hash, vote_value) VALUES
(1, 'anon_voter_01', 1),
(1, 'anon_voter_02', 1),
(1, 'anon_voter_03', 1),
(2, 'anon_voter_01', 1),
(4, 'anon_voter_04', 1),
(5, 'anon_voter_02', 1);

-- ---------------------------------------------------------------------------
-- 7. REVIEW RESPONSES (Anonymous Classmate / Peer Tips)
-- ---------------------------------------------------------------------------
INSERT OR IGNORE INTO review_responses (review_id, responder_label, response_text, client_fingerprint_hash) VALUES
(1, 'Classmate Tip', 'Totally agree! Don''t skip the Friday review sheets—they give extra credit!', 'anon_resp_01');
