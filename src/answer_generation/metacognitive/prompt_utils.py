
PROMPTS = {
 'english': [ 
    'You have to select one of these options:',
    "You have to answer the following multiple choice question.",
    "You must select only one option.",
    "question is",
    "You may select more than one option",
    "Here are the options:",
    "You have to answer the following open answer question.",
    """As you perform this task, follow these steps:
    1. Clarify your understanding of the question.
    2. Make a preliminary identification of relevant concepts and strategies necessary to answer this question, and propose an answer.
    3. Critically assess your preliminary analysis. If you are unsure about its correctness, try to reassess the problem.
    4. Confirm your final answer and explain the reasoning behind your choice.""",
    "Provide the answer in your final response as \"Final answer is [your selected option] \" ",
    "Provide the answer in your final response as \"Final answer is [your selected options] \" ",
    "Provide the answer in your final response as \"Final answer is \" ",
    "You are an expert.",
    "You are an expert in "
 ],
 'french':[ # To use on all questions
    'Vous devez sélectionner l\'une des options suivantes:',
    "Vous devez répondre à la question à choix multiples suivante.",
    "Vous devez choisir une seule option.",
    "la question est",
    "Vous pouvez sélectionner plus d'une option",
    "Voici les options :",
    "Vous devez répondre à la question suivante.",
    """Pour effectuez cette tâche, suivez les étapes suivantes :
    1. Clarifiez la question telle que vous la comprenez.
    2. Effectuez une identification préliminaire des concepts importants et des stratégies nécessaires pour répondre à cette question, et proposez une réponse.
    3. Évaluez de manière critique votre analyse préliminaire. Si vous n'êtes pas sûr de sa justesse, essayez de réévaluer le problème.
    4. Confirmez votre réponse finale et expliquez le raisonnement derrière votre choix.""",
    "Fournissez votre réponse finale en indiquant \"La réponse finale est [votre option choisie]\" ",
    "Fournissez votre réponse finale en indiquant \"La réponse finale est [vos options choisie]\" ",
    "Fournissez votre réponse finale en indiquant \"La réponse finale est \" ",
    "Tu es un expert.",
    "Tu es un expert en "
 ],
 'en-with-fr-language':[ # To use only on questions in French
    'You have to select one of these options:',
    "You have to answer the following multiple choice question in French.",
    "You must select only one option.",
    "question is",
    "You may select more than one option",
    "Here are the options:",
    "You have to answer the following open answer question in French.",
    """As you perform this task, follow these steps in French:
    1. Clarify your understanding of the question.
    2. Make a preliminary identification of relevant concepts and strategies necessary to answer this question, and propose an answer.
    3. Critically assess your preliminary analysis. If you are unsure about its correctness, try to reassess the problem.
    4. Confirm your final answer and explain the reasoning behind your choice in French.""",
    "Provide the answer in your final response in French, as \"La réponse finale est [your selected option] \" ",
    "Provide the answer in your final response in French, as \"La réponse finale est [your selected options] \" ",
    "Provide the answer in your final response in French, as \"La réponse finale est \" ",
    "You are an expert.",
    "You are an expert in "
 ],
'fr-with-en-language':[ # To use only on questions in English
    'Vous devez sélectionner l\'une des options suivantes:',
    "Vous devez répondre à la question à choix multiples suivante en anglais.",
    "Vous devez choisir une seule option.",
    "la question est",
    "Vous pouvez sélectionner plus d'une option",
    "Voici les options :",
    "Vous devez répondre à la question suivante en anglais.",
    """Pour effectuez cette tâche, suivez les étapes suivantes en anglais :
    1. Clarifiez la question telle que vous la comprenez.
    2. Effectuez une identification préliminaire des concepts importants et des stratégies nécessaires pour répondre à cette question, et proposez une réponse.
    3. Évaluez de manière critique votre analyse préliminaire. Si vous n'êtes pas sûr de sa justesse, essayez de réévaluer le problème.
    4. Confirmez votre réponse finale et expliquez le raisonnement derrière votre choix en anglais.""",
    "Fournissez votre réponse finale en anglais en indiquant \"Final answer is [votre option choisie]\" ",
    "Fournissez votre réponse finale en anglais en indiquant \"Final answer is [vos options choisie]\" ",
    "Fournissez votre réponse finale en anglais en indiquant \"Final answer is \" ",
    "Tu es un expert.",
    "Tu es un expert en "
 ],
}


def mcq_with_one_correct(question, template):
    """ Generates prompt for multiple choice question with one correct answer """
    question_body = question['question_body']
    options = question['question_options']
    options_txt = '\n' + template[0] + '\n'
    options_txt += template[5] + '\n'
    for i, option in enumerate(options):
        opt = '[' + chr(i + 65) + ']: ' + option + '\n'
        options_txt += opt
    question_prompt = question_body + '\n' + options_txt
    prompt = template[1] + '\n'
    prompt += template[2] + '\n'
    prompt += template[3] + '\n'
    prompt += question_prompt + '\n'
    prompt += template[7] + '\n'
    prompt += template[8]
    return prompt

def mcq_with_multi_correct(question, template):
    """ Generates prompt for multiple choice question with multiple correct answers """
    question_body = question['question_body']
    options = question['question_options']
    options_txt = '\n' + template[4] + '\n'
    options_txt += template[5] + '\n'
    for i, option in enumerate(options):
        opt = '[' + chr(i + 65) + ']: ' + option + '\n'
        options_txt += opt
    question_prompt = question_body + '\n' + options_txt
    prompt = template[1] + '\n'
    prompt += template[4] + '\n'
    prompt += template[3] + '\n'
    prompt += question_prompt + '\n'
    prompt += template[7] + '\n'
    prompt += template[9]
    return prompt

def open_answer(question, template):
    """ Generates prompt for open answer question """
    question_body = question['question_body']
    question_prompt = question_body + '\n'
    prompt = template[6] + '\n'
    prompt += template[3] + '\n'
    prompt += question_prompt + '\n'
    prompt += template[7] + '\n'
    prompt += template[10]
    return prompt


def get_prompt(question, prompt_lang, course_lang):
    """ Generates prompt for a question """
    if prompt_lang == 'inverted':
        if course_lang == 'english':
            template = PROMPTS['fr-with-en-language']
        elif course_lang == 'french':
            template = PROMPTS['en-with-fr-language']
    else:
        template = PROMPTS[prompt_lang]
    question_type = question['question_type']
    if question_type == 'mcq':
        multiple = question['multiple_correct_answers']
        if not multiple:
            prompt = mcq_with_one_correct(question, template)
        else:
            prompt = mcq_with_multi_correct(question, template)
    else:
        prompt = open_answer(question, template)
    return prompt


def get_system_message(question, prompt_lang, course_lang):
    """ Generates system message for a question """
    if prompt_lang == 'inverted':
        if course_lang == 'english':
            template = PROMPTS['fr-with-en-language']
        elif course_lang == 'french':
            template = PROMPTS['en-with-fr-language']
    else:
        template = PROMPTS[prompt_lang]
    course_name = question["course_name"]
    message = template[-1] + course_name + '.'
    return message