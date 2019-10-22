# Generic autograder scripts.
## prepare_data.py
This script extracts the zip file downloaded from moodle and stores directories named with different roll numbers / team names
Just supply it the correct regex in `SUBMISSION_NAME` variable. 

For example, if students have been asked to submit their files as `outlab4-team_name.tar.gz`, then it will create a directory (you can specify its name with `--extract_dir`). In `extract_dir`, it will create a folder for each student with the name `team_name` and will put all the files extracted from the student's submission into that folder.

You can choose to extract all of the students' submissions. To do that, supply `--grade_all True`. It will also create a file (let's call it roll list) containing the list of team names whose submissions were present. You can specify its name with argument `--roll_list`. If you pass `--grade_all False`, then instead of writing into the roll list, it will only extract those submissions which are present in the roll list.

## grade.py

This script runs your autograders for different questions for all students.

1. For each question, create a directory and keep all your grading material for that question (eg: autograding script) there.
2. Fill in different variables in the script. For each question, you need to specify certain things. Some of them are:
   - `QUESTIONS`: names of questions that will be checked (This will go to the header of output tsv)
   - `MASK`: Boolean mask whether to grade a question or not.
   - `FILES`: Files that need to be copied from 1 student's submission.
   - `BACK_FILES`: Files that need to be copied back. These files will be copied back to location specified in `BACK_FILES_DEST` AFTER autograder has been runned.
   - `COMMANDS`: Commmand to be executed, one for each question. The command **should terminate after printing just the marks obtained**, if AUTOGRADE is True for that question.
   - `LOCATIONS`: a location where all relevant files (autograder, testcases, etc) for that question are present.
   - `AUTOGRADE`: Boolean list; If False, it will give a prompt after running your autograder. You can specify your marks there.

3. Then run it! Some arguments are:
   - `--roll_list`: The list of roll numbers/team names that need to be graded. 
   - `--marks`: Marks will be put in this file
   - `--extract_dir`: The directory where all the folders have been extracted. This should be the same argument that you supplied to `grade.py`.
   - `--order`: This should be one of {`student`, `question`}. If it is `student`, then it will grade all questions of each student and then move to next. Else, It will grade a particular question for all students and then move to next question.

## credits
- Aryan
- Yash Shah