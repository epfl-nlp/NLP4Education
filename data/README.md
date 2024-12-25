# Dataset README

[![License: CC BY-NC-ND](https://img.shields.io/badge/License-CC%20BY--NC--ND-blue.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)

All data is released under [CC-BY-NC-ND](https://creativecommons.org/licenses/by-nc-nd/4.0/deed.en) license, except online courses, which are released under [CC-BY](https://creativecommons.org/licenses/by/4.0/) license. 

To prevent potential leakage of the gold answers and as the original course names are not critical to the analyses, we have anonymized the course names to prioritize privacy and data integrity.

Here are the files provided for the dataset:

- `courses.json` which has information on each unique course and their ID **(NOTE: SOME COURSES HAVE BEEN REMOVED AT THE REQUEST OF THE DATA PROVIDER)** 
    - `course_id`: the unique course ID
    - `course_name`: the anonymized course name
    - `course_program`: the program/topic of the course
    - `course_language`: the language the course is evaluated in
    - `course_year`: whether it is `bachelor`, `master`, or `online` course

- `questions.json` which has information on each unique question, their ID, their type, and the corret answer to the question. **(NOTE: SOME QUESTIONS AND/OR GOLD ANSWERS HAVE BEEN REMOVED AT THE REQUEST OF THE DATA PROVIDER)** 
    - `question_id`: the unique question ID
    - `course_id`: the ID of the course it belongs to
    - `question_type`: `mcq` or `open_answer`
    - `question_body`: question body
    - `question_options`: if MCQ, answer options
    - `question_sub_type`: if MCQ, how many answers choose
    - `mcq_answer_index`: if MCQ, the correct answer options index.
    - `question_answer`: the correct answer
    - `multiple_correct_answers`: if MCQ, a flag to note whether multiple answers are correct
    - `question_explanation`: (optional) more information/explanation for the answer
    - `question_difficulty`: (optional) difficulty of the question
    - `blooms_rating`: (optional) blooms category of the question

- `grade_per_question.csv` is a csv file that has a more convenient format for analyzing grades per question_id,model,prompt_type and includes all prompting styles.
    - Each entry in this table are the same as the ones above: course_id, question_id, question_type, prompt_type, model, correct_mcq_index,m odel_selected_mcq_index, grade,language, program, year
