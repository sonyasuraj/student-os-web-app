from datetime import datetime
teacher_in_system=True
correct_answer=False
grade_list=["a","b","c","d","f"]
course_list=["m","e","s","h","pe","o"]
#user_id(fetched from user acount)
#teacher_id(fetched from teachers table)
first_name_teacher=input("What is the teachers first name? > ").strip()
if str(first_name_teacher) and first_name_teacher!= "":
    correct_answer=True
else:
    while correct_answer== False:
        first_name_teacher=input("(Try again)What is the teachers first name? > ").strip()
        if str(first_name_teacher) and first_name_teacher!= "":
            correct_answer=True
        else: 
            correct_answer=False

correct_answer=False            
last_name_teacher=input("What is the teachers last name? > ").strip()
if str(last_name_teacher) and last_name_teacher!= "":
    correct_answer=True
else:
    while correct_answer== False:
        last_name_teacher=input("(Try again)What is the teachers last name? > ").strip()
        if str(last_name_teacher) and last_name_teacher!= "":
            correct_answer=True
        else: 
            correct_answer=False
#user_district(pulled from user table)
#Check if teacher is found in system
#If NOT then redirect to ask if to make a new teacher to be put into the system

correct_answer=False
teacher_course= input("What is your teachers course name (M for math, E for english, S for science, H for history, PE for physical education, O for other)> ").strip().lower()
if teacher_course in course_list:
        correct_answer=True
else:
    while correct_answer== False:
        teacher_course=input("(Try again)What is your teachers course name (M for math, E for english, S for science, H for history, PE for physical education, A for art, O for other)> ").strip().lower()
        if teacher_course in course_list:
            correct_answer=True
        else: 
            correct_answer=False

if teacher_in_system== True:

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
           
    correct_answer=False            
    time_of_review= datetime.now()
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
    #grade_level(fetched from user acount)
    #reveiw_id(system generated)
    #status(AI will check if the message will be deemed apropriate, in which if it isn't it will be flagged to be checked by a human moderator)

if teacher_in_system==False:
    print("")

