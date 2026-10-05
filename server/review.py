#
# review.py  
# save a review for a teacher who is already in the database
# save a review and the teacher if teacher is not found
# get all reviews for a teacher
#

import secrets
import db_gateway
import dispatcher
import constants
from moderation import check_review
from db_gateway import add_review

def save_review(teacher_id, rating_overall, rating_difficulty, rating_helpfulness,review_text, client_fingerprint_hash, course_name,reviewer_role, student_grade_level, tag_ids):
    review_status, error_message =check_review(review_text)
    print ("Review status from moderation step: " + review_status)
    
    if review_status == constants.DECLINE or review_status == constants.RETRY: 
        return review_status, error_message
    
    success, review_id, error_message=add_review(
                teacher_id=teacher_id,
                rating_overall=rating_overall,
                rating_difficulty=rating_difficulty,
                rating_helpfulness=rating_helpfulness,
                review_text=review_text,
                client_fingerprint_hash=client_fingerprint_hash,
                course_name=course_name,
                reviewer_role=reviewer_role,
                student_grade_level=student_grade_level,
                tag_ids=tag_ids
    )

    if success == True:
        review_status = constants.ALLOW
    else:
        review_status = constants.DECLINE

    return review_status, review_id, error_message;


tup="call moderation then if passed call db_gateway"