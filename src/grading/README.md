# Grading Open-ended Questions


## Usage

Grading open-ended questions by GPT4 as a grader with the following arguments:

**data_file_path**: Questions with their generated answers
**course_info_file_path**: Course information json file (required).
**output_file_path**: Output file to save graded questions (required).
**api_key**: OpenAI API key (required)
**organization**: OpenAI organization (required)



```
python grade_open_answer.py \
    --data_file_path generated_answers.json \
    --course_info_file_path courses.json \
    --output_file_path graded_questions.json \
    --api_key OPENAI_API_KEY \
    --organization OPENAI_ORGANIZATION \
```