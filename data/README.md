# Dataset README

[![License: CC BY-NC-ND](https://img.shields.io/badge/License-CC%20BY--NC--ND-blue.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)
[![License: CC-BY](https://img.shields.io/badge/License-CC--BY-blue.svg)](https://creativecommons.org/licenses/by/4.0/)

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

> **Note:** You can gather all models answers together by doing `python gather_answers.py`
- `model_answers.json` which has the answer for each prompt and model pair for every question in `questions.json` **NOTE: SELF-REFINE AND EXPERT PROMPTING HAVE BEEN REMOVED FOR ANONYMITY PURPOSES, BUT THE GRADES FOR THESE PROMPTING STRATEGIES HAVE BEEN PROVIDED IN THE NEXT CSV FILE**
    - `question_id`: the unique question ID
    - `model_name`: the prompted model -- can be ['gpt-4', 'gpt-3.5-turbo']
    - `prompt_type`: the prompt type -- can be [tree_of_thought', 'zero_shot', 'cot_zero_shot', 'one_shot', 'metacog', 'cot_four_shot']
    - `question_type`: `mcq` or `open_answer`
      
    - `question_body`: question body
    - `mcq_answer_index`: if MCQ, the correct answer options index

    - `question_options`: if MCQ, answer options
    - `selected_options`: if MCQ, the answer index selected by the model

    - `prompt_text`: the input prompt
    - `model_output`: the model's answer

    - `direct_gpt4_prompt` or `grade_prompt`: if open answer, the prompt given to the gpt4 model for grading, it's the former if it doesn't require a system prompt
    - `grade_output`: if open answer, the answer to the grade prompt
    - `direct_gpt4_score`: if open answer, the label extracted for the grade
    - `grade`: if open answer, the numerical score of `direct_gpt4_score`

- `grade_per_question.csv` is a csv file that has a more convenient format for analyzing grades per question_id,model,prompt_type and includes all prompting styles.
    - Each entry in this table are the same as the ones above: course_id, question_id, question_type, prompt_type, model, correct_mcq_index,m odel_selected_mcq_index, grade,language, program, year
