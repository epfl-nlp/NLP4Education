import logging
import argparse
import os
import time 
import json

from prompt_utils import get_prompt, get_system_message

import openai
from tqdm import tqdm
from torch.utils.data import DataLoader

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("generator")

generator_models = {
    "gpt-3-002": "text-davinci-003",
    "gpt-3-003": "text-davinci-003",
    "chatgpt": "gpt-3.5-turbo",
    "gpt-4": "gpt-4",
}

def load_json_file(input_file):
    """ Load json file """
    with open(input_file) as f:
        data = json.load(f)
    return data

class Generator:
    def __init__(self, args):
        self.args = args
        self.generation_outputs = []
        self.num_records = 0
        self.prompt_type = None

        self.generation_modes = {
            "completion": self.completion,
            "chat": self.chat,
        }

        self.failed_examples = []
        self.init_generator_model(args)


    def init_generator_model(self, args):
        assert args.gen_mode in self.generation_modes.keys(), "Invalid generation mode!"
        self.gen_mode = args.gen_mode

        assert args.engine in generator_models.keys(), "Invalid model name!"
        if self.gen_mode == "completion":
            assert (
                not args.engine == "chatgpt"
            ), "ChatGPT model does not support completion mode!"
            assert (
                not args.engine == "gpt-4"
            ), "GPT-4 model does not support completion mode!"
        elif self.gen_mode == "chat":
            assert (
                not args.engine == "gpt-3-002"
            ), "GPT-3-002 model does not support chat mode!"
            assert (
                not args.engine == "gpt-3-003"
            ), "GPT-3-003 model does not support chat mode!"

        self.model = generator_models[args.engine]
        self.generator = self.generation_modes.get(self.gen_mode)

    def preprocess(self, querys):
        logger.info(f"Querying {len(querys)} problems from DB ...")
        dataloader = DataLoader(
            querys, batch_size=4, shuffle=False, collate_fn=lambda x: x
        )

        self.dataloader = dataloader
        self.num_records = len(querys)

    def completion(self, prompt):
        response = openai.Completion.create(
            model=self.model,
            prompt=f"{prompt['instruction']}\n{prompt['problem']}",
            top_p=self.args.top_p,
            temperature=self.args.temperature,
            max_tokens=self.args.max_tokens,
            frequency_penalty=self.args.frequency_penalty,
            presence_penalty=self.args.presence_penalty,
        )
        return response["choices"][0]["text"]

    def chat(self, prompt):
        messages = []
         # Create the system message
        course_lang = self.args.courses_info[prompt["problem"]["course_id"]]["course_language"].lower()
        q = prompt["problem"]
        q["course_name"] = self.args.courses_info[q["course_id"]]["course_name"]  
        system_instruction = get_system_message(q, self.args.prompt_language, course_lang)
        messages.append({"role": "system", "content": system_instruction})

        # Create the prompt
        prompt_content = get_prompt(q, self.args.prompt_language, course_lang).strip()
        messages.append({"role": "user", "content": prompt_content})

        # Generate model output
        response = openai.ChatCompletion.create(
            model=self.model, 
            messages=messages,
            top_p=self.args.top_p,
            temperature=self.args.temperature,
            max_tokens=self.args.max_tokens,
            frequency_penalty=self.args.frequency_penalty,
            presence_penalty=self.args.presence_penalty,
        )
        output_text = response["choices"][0]["message"]["content"]

        output = {
            "question_id": prompt["problem"]["question_id"],
            "model_output": output_text,
            "prompt_type": self.args.prompt_type,
            "prompt_language": self.args.prompt_language,
            "prompt_text": messages,
            "model.name": self.model,
        }
        return output
        

    def postprocess(self, output, record):
        output = output.replace("\n", "").strip()
        record["response"] = output
        return record

    def batch_generate(self, querys):
        self.preprocess(querys)

        logger.info(f"Prompting {self.num_records} problems ...")
        generation_outputs = []

        for batch in tqdm(self.dataloader):
            batch_outputs = self.generate(batch)
            logger.info(f"Collecting {len(batch_outputs)} generation ...")
            generation_outputs.extend(batch_outputs)

        logger.info(f"Total {len(generation_outputs)} generation outputs collected")
        return generation_outputs

    def generate(self, batch):
        batch_generation_outputs = []
        for query in batch:
            try:
                response = self.generator(query)
                batch_generation_outputs.append(response)
            except:
                # Keep track of failed examples to try again later
                self.failed_examples.append(query)
                course_id = query["problem"]["course_id"]
                logger.info(f"Error in generating response for {query} in course {course_id}")
                continue
            
        return batch_generation_outputs

def generate_questione_batches(questions, batch_size=100):
    """ Create a batch of questions """
    batch_size = min(batch_size, len(questions))
    batches = []
    for i in range(0, len(questions), batch_size):
        batches.append(questions[i:i+batch_size])
    if (i+1)*batch_size < len(questions):
        batches.append(questions[i:])
    return batches

def parse_args():
    parser = argparse.ArgumentParser(description="Metacognitive Prompting")
    parser.add_argument("--gen_mode", type=str, default="chat")
    parser.add_argument("--engine", type=str, default="chatgpt")
    parser.add_argument("--max_tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top_p", type=float, default=1.0)
    parser.add_argument("--frequency_penalty", type=float, default=0.8)
    parser.add_argument("--presence_penalty", type=float, default=0.5)
    parser.add_argument("--data_file_path", type=str, help='Input file path', required=True)
    parser.add_argument("--courses_info_file_path", type=str, help='Courses information file path.' , required=True)
    parser.add_argument("--output_file_path", type=str, help='Output file path', required=True)
    parser.add_argument("--api_key", type=str, default="", required=True)
    parser.add_argument("--organization", type=str, default="", required=True)
    parser.add_argument("--prompt_type", type=str, default="metacognitive")
    parser.add_argument("--prompt_language", type=str, default="english")

    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    openai.api_key = args.api_key
    openai.organization = args.organization
    
    # Read courses information
    courses_info_list = load_json_file(args.courses_info_file_path)
    courses_info = {}

    for c in courses_info_list:
        courses_info[c["course_id"]] = c

    args.courses_info = courses_info

    start = time.time()
    generator = Generator(args)

    questions = load_json_file(args.data_file_path)
    
    logger.info(f"Generating responses for {args.prompt_type} prompting and for {args.engine} model ...\n")

    if os.path.exists(args.output_file_path):
        with open(args.output_file_path) as f:
            done_responses = json.load(f)

        if len(questions) != len(done_responses):
            done_questions = [q["question_id"] for q in done_responses]
            questions = [q for q in questions if q["question_id"] not in done_questions]
        else:
            logger.info(f"Already fully done!")
            return
    else: 
        done_responses = []

    logger.info(f"Total {len(questions)} questions to be processed\n")
    output_responses = []
        
    querys = []
    for i, q in enumerate(questions):
            query = {"problem": q}
            querys.append(query)

    # Create batches of questions
    batched_questions = generate_questione_batches(querys, batch_size=100)

    for i, q_batch in enumerate(batched_questions):
        output_responses += generator.batch_generate(q_batch)
        logger.info(f"Done with batch {i+1}/{len(batched_questions)} ({(i+1)*len(q_batch)} questions) ....")

        with open(args.output_file_path, "w") as f:
            json.dump(output_responses, f, indent=2, ensure_ascii=False)

    output_responses += done_responses

    with open(args.output_file_path, "w") as f:
        json.dump(output_responses, f, indent=2, ensure_ascii=False)

    failed_questions_file = args.output_file_path.replace(".json", "_failed.json")
    with open(failed_questions_file, "a+") as f:
        json.dump(generator.failed_examples, f, indent=2, ensure_ascii=False)


    logger.info(f"{len(querys)} questiones are processed in {time.time() - start :.2f} seconds.")
    print("************************************************************")

if __name__ == "__main__":
    main()
    
    
