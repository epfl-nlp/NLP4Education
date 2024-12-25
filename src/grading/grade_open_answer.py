import json
import argparse
import openai
import re
import time
import logging


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("Open Answer Grader")

GRADES = ['correct', 'almostcorrect', 'mostlyincorrect', 'wronganswer']


def load_json_file(input_file):
    """ Load json file """
    with open(input_file) as f:
        data = json.load(f)
    return data

def get_system_message(question):
    """
    Getting instruction for openAI models
    """
    course_id = question['course_id']
    course_name = question["course_name"]
    if course_name is None:
        message = "You are a teacher assessing an exam. You must grade exam questions."
    else:
        message = f"You are a teacher of {course_name}. You must grade exam questions."
    return message


def get_prompt(answer_to_grade, full_question):
    """
    getting the grading prompt
    to use a different prompt, this method should be changed
    """
    question = full_question['question_body']
    correct_answer = full_question['question_answer']
    given_answer = answer_to_grade['model_output']
    prompt = f"""You must rigorously grade an exam question. Please be strict and precise in your assessment, providing reasoning for your assigned grade. Here's the process I'd like you to follow:
    Carefully read and understand the question.
    Thoroughly compare the student's answer with the correct golden answer.
    Evaluate the student's response based on its accuracy and completeness.
    Deduce a final grade by considering whether the answer is 'wrong answer', 'mostly incorrect', 'almost correct', 'correct', along with a clear explanation for your decision.
    Question: {question}
    Golden Answer: {correct_answer}
    Student Answer: {given_answer}
    """
    prompt += """
    format your answer in in the following json format, providing a clear and detailed evaluation for each of the two criterion (accuracy and completeness) and finally providing the grade. in the field of grade only write the final grade from given grading options.:
    {"accuracy": ,
    "completeness": ,
    "grade":
    }
    """
    return prompt


def extract_grade(grading_output):
    """
    The model is asked to give the final grade in a specific json format
    this method extracts the grade from the model output, according to the format
    however, sometimes model outputs are not in the correct format
    to fix those rare cases, fix_finial_grades.py is used
    """
    grading_output = grading_output.replace(' ', '').replace('\n', '').lower().strip()
    pattern = r'"grade":"(.*?)"'
    match = re.search(pattern, grading_output)

    if match:
        result = match.group(1)
    else:
        pattern = r'grade:"(.*?)"'
        match = re.search(pattern, grading_output)
        if match:
            result = match.group(1)
        else:
            result = "not found"
    if result == 'mostlycorrect':
        result = 'almostcorrect'
    if result not in GRADES:
        result = "not found"
    return result


def prompt_openai(messages):
    flag = True
    while flag:  # while getting exception from API, retry
        try:
            response = openai.ChatCompletion.create(model='gpt-4',
                                                    messages=messages,
                                                    top_p=1.0,
                                                    temperature=0.8,
                                                    frequency_penalty=0.8,
                                                    presence_penalty=0.5,
                                                    )
            flag = False
        except Exception as e:
            logger.error(f"The following error has happened:\n{e}")
            logger.info(f"Waiting for 5 seconds...")
            time.sleep(5)
    return response


def grade(answer_to_grade, full_question):
    """ Grading a single question """
    # getting the messages to the model
    instruction = get_system_message(full_question)
    prompt = get_prompt(answer_to_grade, full_question)
    messages = [{"role": "system", "content": instruction}]
    messages.append({"role": "user", "content": prompt})

    # asking the model to grade 
    response = prompt_openai(messages)
    grading_output = response['choices'][0]['message']['content']

    graded_output = {k:v for k, v in full_question.items() if k in ['question_id', 'question_type', 'course_id',
                                                                    'question_body', 'question_answer']}
    graded_output.update({k: answer_to_grade[k] for k in ['prompt_type', 'model_output']})
    graded_output['model'] = answer_to_grade['model.name']
    graded_output['grade_instruction'] = instruction
    graded_output['grade_output'] = grading_output
    answer_grade = extract_grade(grading_output)

    # additional feedback api call
    if answer_grade == 'not found':
        logger.info(f"Could not extract grade from the following output:\n{grading_output}. Trying again.")
        feedback = "Answer with only the grade you are giving to the student. Choose only from: 'wrong answer', 'mostly incorrect', 'almost correct', 'correct'."
        messages.append({"role": "assistant", "content": grading_output})
        messages.append({"role": "user", "content": feedback})
        response = prompt_openai(messages)
        grading_output = response['choices'][0]['message']['content']
        answer_grade = grading_output.replace(' ', '').lower()
        if answer_grade not in GRADES:
            answer_grade = 'not found'

    graded_output['direct_gpt4_score'] = answer_grade
    graded_output['grade_prompt'] = messages

    if graded_output['direct_gpt4_score'] == 'not found':
        logger.warning(f"Could not extract grade from the following output:\n{grading_output}")
    return graded_output

def parse_args():
    parser = argparse.ArgumentParser("Direct grading of open answer questions (GPT4 as a grader)")

    parser.add_argument("--data_file_path", type=str, help='Input file path', required=True)
    parser.add_argument("--courses_info_file_path", type=str, help='Courses information file path.' , required=True)
    parser.add_argument("--output_file_path", type=str, help='Output file path', required=True)
    parser.add_argument("--api_key", type=str, default="", required=True)
    parser.add_argument("--organization", type=str, default="", required=True)

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    logger.info('starting the grading')

    args = parse_args()

    openai.api_key = args.api_key
    openai.organization = args.organization

    courses_info_list = load_json_file(args.courses_info_file_path)
    courses_info = {}

    for c in courses_info_list:
        courses_info[c["course_id"]] = c

    input_data = load_json_file(args.data_file_path)

    graded_questions = []
    for question in input_data:
        question['course_name'] = courses_info[question["course_id"]]["course_name"]
        answer_to_grade = question["model_answer"] # this is the answer generated by the model (a dict with `model_output` and `model.name`)
        graded_output = grade(answer_to_grade, question)
        graded_questions.append(graded_output)

    with open(args.output_file_path, 'w') as f:
        json.dump(graded_questions, f, indent=4, ensure_ascii=False)
