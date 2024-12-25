import ast
import string

INSTRUCTIONS = {"mcq": {"single": "You are given a question followed by the possible answers. Only one answer is correct. First give the reasoning and then output the correct answer.",
         "multi": "You are given a question followed by the possible answers. The question can have multiple correct choices. First give the reasoning and then output all the correct answers."},
  "open_answer": "Solve the following question:",
  "system": "You are a Professor of Computer Science."}


def get_system_message(query):
    """  Generates system message for the given query. """
    course_name = query["course_name"]
    sys_message = {"role": "system", "content": f"You are an expert in {course_name}"}
    return sys_message


def create_question_content(prompt):
    """  Generates prompt for the given question."""

    if prompt["question_type"] != "mcq":
        raise NotImplementedError("Open-ended questions are currently not supported.")

    else: # mcq questions
        if type(prompt["question_answer"]) == str:
            prompt_answer = ast.literal_eval(prompt["question_answer"])
        elif type(prompt["question_answer"]) == int:
            answer_index = prompt["question_answer"]
            prompt_answer = [prompt["question_options"][answer_index]]
        else:
            raise ValueError(f"Type {type(prompt['question_answer'])} for question_answer is not expected.")

        if len(prompt_answer) == 1:  # only one answer is correct
            prefix = INSTRUCTIONS["mcq"]["single"]
        else:
            prefix = INSTRUCTIONS["mcq"]["multi"]
        english_alphabet = string.ascii_uppercase
        choices_text = "\n".join([f"{english_alphabet[index]}: {option}"
                                  for index, option in enumerate(prompt["question_options"])])
        question_content = f"{prefix}\nQuestion: {prompt['question_body']}\n{choices_text}"
        return question_content
