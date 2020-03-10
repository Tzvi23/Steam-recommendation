from EvaluationContentTesting import content_evaluation_summary
from EvaluationFeatureTesting import run_feature_testing
from SystemEvalutionTesting import eval_similarUser

numberOfTests = 5
print('1) Feature Recommendation Evaluation')
print('2) Content Recommendation Evaluation')
print('3) Similar Recommendation Evaluation')
choice = int(input('Choose option: '))

"""
We evaluate each recommendation system based on
'Leave One Out' approach. Each system chooses random user and than
chooses random game to remove from the user list, and than checks
if in the recommended games the removed game exists.
"""

if choice == 1:
    run_feature_testing()
elif choice == 2:
    content_evaluation_summary(numberOfTests)  # Because of time complexity the system runs loops of 5 random users chosen
elif choice == 3:
    eval_similarUser(numberOfTests)
else:
    choice2 = input('Run all? [y/n]')
    if choice2 is 'y':
        print(' ~~~~~~~~~~~~~~~~~~ Starting Feature Evaluation ~~~~~~~~~~~~~~~~~~')
        run_feature_testing(numberOfTests)
        print(' ###################### Feature Evaluation Ended ######################')
        print(' ~~~~~~~~~~~~~~~~~~ Starting Content Evaluation ~~~~~~~~~~~~~~~~~~')
        content_evaluation_summary(numberOfTests)
        print(' ###################### Content Evaluation Ended ######################')
        print(' ~~~~~~~~~~~~~~~~~~ Starting Similar Users Evaluation ~~~~~~~~~~~~~~~~~~')
        eval_similarUser(numberOfTests)
        print(' ###################### Similar Users Evaluation Ended ######################')
        print('[!!] Finished Evaluation')
    else:
        print('The end :(')
