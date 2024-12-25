
def mcq_with_one_correct(question):
    """  Generate prompt for an MCQ with one correct answer.
    Args:
        question (dict): question dictionary
    """
    question_body = question['question_body']
    options = question['question_options']

    options_txt = '\nYou have to select one of these options:\n'
    options_txt += 'Here are the options:\n'
    for i, option in enumerate(options):
        opt = '[' + chr(i + 65) + ']: ' + option + '\n'
        options_txt += opt

    question_prompt = question_body + '\n' + options_txt
    prompt = f"""
    Imagine three different experts answering this multiple-choice question.
    They will brainstorm the answer step by step reasoning carefully and taking all facts into consideration
    All experts will write down 1 step of their thinking,
    then share it with the group.
    They will each critique their response, and all the responses of others
    They will check their answer based on science
    Then all experts will go on to the next step and write down this step of their thinking.
    They will keep going through steps until they reach their conclusion taking into account the thoughts of the other experts
    If at any time they realize that there is a flaw in their logic they will backtrack to where that flaw occurred
    If any expert realizes they're wrong at any point then they acknowledge this and start another tree of thought
    Each expert will assign a likelihood of their current assertion being correct
    Continue until the experts agree on the single most likely answer.
    Provide the answer in your final response as \"Final answer is [your selected option] \"
    The question is \n {question_prompt}
    """
    return prompt


def mcq_with_multi_correct(question):
    """  Generates prompt for an MCQ with multiple correct answers.
     Args:
        question (dict): question dictionary
    """
    question_body = question['question_body']
    options = question['question_options']
    options_txt = '\nYou may select more than one option:\n'
    options_txt += 'Here are the options:\n'
    for i, option in enumerate(options):
        opt = '[' + chr(i + 65) + ']: ' + option + '\n'
        options_txt += opt
    question_prompt = question_body + '\n' + options_txt
    prompt = f"""
    Imagine three different experts answering this multiple-choice question.
    They will brainstorm the answer step by step reasoning carefully and taking all facts into consideration
    All experts will write down 1 step of their thinking,
    then share it with the group.
    They will each critique their response, and all the responses of others
    They will check their answer based on science
    Then all experts will go on to the next step and write down this step of their thinking.
    They will keep going through steps until they reach their conclusion taking into account the thoughts of the other experts
    If at any time they realize that there is a flaw in their logic they will backtrack to where that flaw occurred
    If any expert realizes they're wrong at any point then they acknowledge this and start another tree of thought
    Each expert will assign a likelihood of their current assertion being correct
    Continue until the experts agree on the single most likely answer. 
    Provide the answer in your final response as \"Final correct answers are [your selected options] \"
    The question is \n {question_prompt}
    """
    
    return prompt


def open_ended_answer(question):
    """  Generates prompt for an open-ended answer question.
     Args:
        question (dict): question dictionary
    """
    question_body = question['question_body']
    question_prompt = question_body + '\n'
    prompt = f"""
    Imagine three different experts answering this open answer question.
    They will brainstorm the answer step by step reasoning carefully and taking all facts into consideration
    All experts will write down 1 step of their thinking,
    then share it with the group.
    They will each critique their response, and all the responses of others
    They will check their answer based on science and the laws of physics
    Then all experts will go on to the next step and write down this step of their thinking.
    They will keep going through steps until they reach their conclusion taking into account the thoughts of the other experts
    If at any time they realize that there is a flaw in their logic they will backtrack to where that flaw occurred
    If any expert realizes they're wrong at any point then they acknowledge this and start another tree of thought
    Each expert will assign a likelihood of their current assertion being correct
    Continue until the experts agree on the single most likely answer. 
    Provide the answer in your final response as \"Final answer is \"
    The question is \n {question_prompt}
    """
    return prompt


def get_prompt(question):
    """  Generates prompt for the given question.
    Args:
        question (dict): question dictionary with the following keys: question_id, course_id, question_type, question_body, question_options, question_sub_type, mcq_answer_index, question_answer, multiple_correct_answers, question_explanation
    """
    question_type = question['question_type']
    if question_type == 'mcq':
        if not question['multiple_correct_answers']:
            prompt = mcq_with_one_correct(question)
        else:
            prompt = mcq_with_multi_correct(question)
    elif question_type == 'open_answer':
        prompt = open_ended_answer(question)
    else:
        raise ValueError(f"Invalid question type: {question_type}")
    return prompt