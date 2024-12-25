import string
import json
import random
import os

PROMPT_INSTRUCTION = {
       "English":{    
            "mcq": 
                   {"single": "You are given a question followed by the possible answers. Only one answer is correct. Give a step-by-step reasoning, and then output the correct answer.",
                   "multi": "You are given a question followed by the possible answers. The question can have multiple correct choices. Give a step-by-step reasoning, and then output all the correct answers."},
            "open_answer": "Solve the following question, by first giving the step-by-step reasoning and then outputing the answer.",
            "system": "You are an expert in",
            "question_labels": ["Question", "Answer", "Answer options", "Explanation"]
       },
       "French":{
            "mcq": {
                   "single": "Voici une question suivie des réponses possibles. Une seule réponse est correcte. Expliquez le raisonnement étape par étape, puis indiquez la réponse correcte.",
                   "multi": "Vous avez une question suivie des réponses possibles. La question peut avoir plusieurs réponses correctes. Expliquez le raisonnement étape par étape, puis indiquez toutes les réponses correctes."
                   },
            "open_answer": "Résolvez la question suivante en expliquant d'abord le raisonnement étape par étape, puis en donnant la réponse.",
            "system": "Vous êtes un expert en",
            "question_labels": ["Question", "Réponse", "Choix de réponse", "Explication"]
            }
}

def read_json(path):
    """ Read json file """
    with open(path, "r") as f:
        data = json.load(f)
    return data

def write_json(data, path):
    """ Write json file """
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_system_message(question, args):
    """ Get the system message for a given query. """
    course_name = args.courses_info[question["course_id"]]["course_name"] 
    sys_message = {"role": "system", "content": f"{args.instructions[question['prompt_language']]['system']} {course_name}."}
    return sys_message

def create_question_prompt(question, args):
    """ Create the question prompt for a given sample. """
    prompt_language = question["prompt_language"]
    question_type = question["question_type"]
    instructions = args.instructions[prompt_language]
    if question_type == 'mcq':
        if question['multiple_correct_answers'] == 0:  # only one answer is correct
            prefix = instructions["mcq"]["single"]
        else:
            prefix = instructions["mcq"]["multi"]
        english_alphabet = string.ascii_uppercase
        choices_text = "\n".join([f"{english_alphabet[index]}: {option}"
                                    for index, option in enumerate(question["question_options"])])
    elif question_type == 'open_answer':
        prefix = instructions["open_answer"]

    question_content = f"{prefix}\n{instructions['question_labels'][0]}: {question['question_body']}"
    if question_type == 'mcq':
        question_content += f"\n{instructions['question_labels'][2]}:{choices_text}"
    return question_content

def create_example_demo_content(sample, args):
    """ Create the demonstration example content for a given sample. """
    prompt_language = sample["prompt_language"]
    instructions = args.instructions[prompt_language]
    cot = f"{instructions['question_labels'][3]}: {sample['best_CoT']['text']}"
    if sample["question_type"] == 'open_answer':
        answer = sample["question_answer"]
        if isinstance(answer, list):
            answer = answer[0] 
    else:
        english_alphabet = string.ascii_uppercase
        answer = ""
        if isinstance(sample["mcq_answer_index"], int):
            sample["mcq_answer_index"] = [sample["mcq_answer_index"]]
        for index in sample["mcq_answer_index"]:
            if index < len(sample["question_options"]):
                answer += f"{english_alphabet[index]}. {sample['question_options'][index]}\n"

    cot += f"\n{instructions['question_labels'][1]}: {answer}"
    return cot


def sample_demonstration(args, question):
    course_id = question["course_id"]
    cot_examples_file_path = os.path.join(args.cot_demo_path, f"{course_id}.json")
    if not os.path.exists(cot_examples_file_path):
        raise ValueError(f"Course {course_id} does not have any CoT examples.")
    with open(cot_examples_file_path, "r") as f:
        examples = f.readlines()
    cot_examples = random.choice(random.sample(examples, args.shots))
    for i in range(len(cot_examples)):
        cot_examples[i]['prompt_language'] = question['prompt_language']
    return cot_examples