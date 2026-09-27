# What needs to be put into Database when review is made:

## Use case 1: submitting a review for a teacher that is in the system
    Users_ID_number - system generated
    Teachers_ID_number - pulled from teachers table
    Teacher_name - pulled from teachers table
    User_district - pulled from user table
    Review_ID_number (a number that is unique to the review - system generated)
    Review_text (the actual text that the user had written)
    Review_rating   (rating out of 5 that the user gives)
    Datetime    (what time the review was made - system timestamp)
    Grade_in_class  (what grade the user got in their class)
    Grade_level (grade of user)
    Status  [if the review was appropriate for the website(pending,rejected,cleared,flaged)] - intial status pending 
    --> AI checks for validity 
        --> if cleared
                change status to cleared
                show comment publicly
                update user on status
        --> if flaged 
                -->Human moderator checks for appropriateness
                    --> if cleared
                            change status to cleared
                            show comment publicly
                            update user on status
                    --> if rejected
                            change status to rejected
                            update user on status
## Use case 2: submiting a review that is not in the system