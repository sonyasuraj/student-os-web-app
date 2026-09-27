#
# review.py  
# save a review for a teacher who is already in the database
# save a review and the teacher if teacher is not found
# get all reviews for a teacher
#

import secrets
import db_gateway
from datetime import datetime
from db_gateway import add_review

#
# STEP 0: the lookup function. Likely to move to db_gateway.py
# def find_teacher(school_id, first_name, last_name):
#     ? Look at get_teacher_by_id(). Which parts can you copy?
#     ? Should this return one teacher or a list? What if two have the same name?
#

grade_list=["a","b","c","d","f"]
course_list=["m","e","s","h","pe","a","o"]
#needed for functions
#
# Main flow
#
def main():
    # 1. Find a teacher
    #    ? Which db_gateway function already gives you teacher info while searching?
    #    As we don't have UI, look at the seeded data in database and get the teacher & school info by name/search
    #    What if we get more than one records back for the search query?
    #    For first attempt - pick the teacher id from the database directly and put it in a variable

    # 2. Ask for the review details (your input functions)
    #    Make a function for each input (course name, rating, review text, grade) you are reading from terminal and move your code mockup_review_system.py to these functions
    #    In the end when everything is fully tested, create a common input utility to replace the repeated while-loops
    #    
        reviewtext = input_reviewtext()
        print("here is what we got: " + reviewtext)
        rating = input_rating()
        print("here is what we got: " + str(rating))
        teachercourse = input_course_name()
        print("here is what we got: " + teachercourse)
        lettergrade = input_letter_grade()
        print("here is what we got: " + lettergrade)
        time_of_review= datetime.now()
    # 3. Call the add_review function
    #    Look at what input you need to pass to the function and if you have everything
    #    What is mandatory vs what is optional
    #    Print the values right before saving
        return add_review(4,rating,1,5,reviewtext,"anonstudent001",teachercourse,"student",7,4)
    # 4. After saving, open the database and see if the review is saved
    #    

pass

def input_reviewtext():

    correct_answer=False            
    review_text=input("What is your reviews comment? > ").strip()
    if str(review_text) and review_text!= "":
        correct_answer=True
    else:
        while correct_answer== False:
            review_text=input("(Try again)What is your reviews comment? > ").strip()
            if str(review_text) and review_text!= "":
                correct_answer=True
            else: 
                correct_answer=False
    return review_text

def input_rating():
    correct_answer=False            
    rating=int(input("What is your rating of this teacher out of five? > ").strip())
    if rating > 0 and rating < 6:
        correct_answer=True
    else:
        while correct_answer== False:
            rating=int(input("(Try again)What is your rating of this teacher out of five? > ").strip())
            if rating > 0 and rating<6:
                correct_answer=True
            else: 
                correct_answer=False
    return rating

def input_course_name():
    correct_answer=False
    teacher_course= input("What is your teachers course name (M for math, E for english, S for science, H for history, PE for physical education, O for other)> ").strip().lower()
    if teacher_course in course_list:
            correct_answer=True
    else:
        while correct_answer== False:
            teacher_course=input("(Try again)What is your teachers course name (M for math, E for english, S for science, H for history, PE for physical education, O for other)> ").strip().lower()
            if teacher_course in course_list:
                correct_answer=True
            else: 
                correct_answer=False
    return teacher_course

def input_letter_grade():
    correct_answer=False            
    user_letter_grade= input ("What grade did you get/have in this teacher's class?(Ex: A,B,C,D,F. NO + or -) > ").strip().lower()
    if user_letter_grade in grade_list:
            correct_answer=True
    else:
        while correct_answer== False:
            user_letter_grade=input("(Try again)What grade did you get/have in this teacher's class?(Ex: A,B,C,D,F. NO + or -) > ").strip().lower()
            if user_letter_grade in grade_list:
                correct_answer=True
            else: 
                correct_answer=False
    return user_letter_grade

if __name__ == "__main__":
    main()