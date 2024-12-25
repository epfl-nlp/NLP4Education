import openai
import logging
import argparse
import os
import time
import tiktoken
import json
from tqdm import tqdm

from torch.utils.data import DataLoader
from prompt_utils import *


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("Chain of Thought Prompting")

generator_models = {
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
        self.failed_examples = []
        self.model = generator_models[args.engine]        

    def preprocess(self, queries):
        dataloader = DataLoader(
            queries, batch_size=self.args.batch_size, shuffle=False, collate_fn=lambda x: x
        )
        self.dataloader = dataloader
        self.num_records = len(queries)

    def generator(self, sample):
        messages = []
        sys_message = get_system_message(sample["problem"], self.args)
        messages.append(sys_message)
        
        # Get instructions with example
        if "examples" in sample:
            for example in sample["examples"]:
                question_content = create_question_prompt(example, self.args)
                messages.append({"role": "user", "content": question_content})
                answer_example_content = create_example_demo_content(example, self.args)
                messages.append({"role": "assistant", "content": answer_example_content})

        # Get the prompt
        question_content = create_question_prompt(sample["problem"], self.args)
        messages.append({"role": "user", "content": question_content})

        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        total_tokens = sum(len(encoding.encode(message["content"])) for message in messages)

        while total_tokens > self.args.max_tokens:
            messages = [messages[0]] + messages[3:]
            total_tokens = sum(len(encoding.encode(message["content"])) for message in messages)

        flag = True
        while flag:  # while getting exception from API, retry
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    top_p=self.args.top_p,
                    temperature=self.args.temperature,
                    frequency_penalty=self.args.frequency_penalty,
                    presence_penalty=self.args.presence_penalty,
                    n=self.args.consistency,
                    )
                flag = False
            except openai.error.InvalidRequestError as e:
                logger.info(f"The following error has happened:\n{e}")
                if e.code == "context_length_exceeded":
                    flag = False
                    continue
                else:
                    logger.info(f"Waiting for 5 seconds...")
                    time.sleep(5)

        output_text = [response["choices"][i]["message"]["content"] for i in range(len(response["choices"]))]
        output_text = output_text[0]

        output = {
                  "question_id": sample["problem"]["question_id"],
                  "prompt_text": messages,
                  "model_output": output_text,
                  "prompt_type": self.args.prompt_type,
                  "model.name": self.model,
                }
        
        return output

    def batch_generate(self, queries):
        self.preprocess(queries)
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
            except Exception as e:
                self.failed_examples.append(query)
                course_id = query["problem"]["course_id"]
                logger.info(f"Error in generating response for question id {query['problem']['question_id']} in course {course_id} due to {e}")
                continue

        return batch_generation_outputs


def parse_args():
    parser = argparse.ArgumentParser(description="Performing CoT prompting for the input dataset.")
    parser.add_argument("--engine", type=str, default="chatgpt")
    parser.add_argument("--max_tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top_p", type=float, default=1.0)
    parser.add_argument("--frequency_penalty", type=float, default=0.8)
    parser.add_argument("--presence_penalty", type=float, default=0.5)
    parser.add_argument("--prompt_type", type=str, default="zero_shot_chain_of_thought")
    parser.add_argument("--api_key", type=str, default="", required=True)
    parser.add_argument("--organization", type=str, default="", required=True)
    parser.add_argument("--data_file_path", type=str, help='Input file path', required=True)
    parser.add_argument("--courses_info_file_path", type=str, help='Courses information file path.' , required=True)
    parser.add_argument("--output_file_path", type=str, help='Output file path', required=True)
    parser.add_argument("--cot_demo_path", type=str, default="generated_CoT_validated", help="path to demonstrations for chain of thought, for each course (cot demosntrations should follow the same format as questions).")
    parser.add_argument("--consistency", type=int, default=1,
                        help="Whether to perform self-consistency or not. If not, input 1 (default). If yes, input number of times the answer is generated. NOT IMPLEMENTED")
    parser.add_argument("--batch-size", type=int, default=4,
                        help="Batch size (1 for debug, 4 otherwise), default is 4")
    parser.add_argument("--sample", type=int, default=0,
                        help="Sampling for debugging, default is 0 (no sampling)")
    parser.add_argument("--prompt_language", type=str, help="Prompt Language: all English, all French, or 'cross'. Stick to English! Language-inverted prompting is done for other strategies.", default="English")
    parser.add_argument("--shots", type=int, help="Number of shots for the CoT demonstrations: from 0 to 4, default is 0", default=0)

    args = parser.parse_args()

    if args.shots == 0:
        args.prompt_type = "zero_shot_chain_of_thought"
    elif args.shots == 4:
        args.prompt_type = "four_shot_chain_of_thought"
    else:
        args.prompt_type = f"CoT_{args.shots}-shot"

    args.prompt_type += f"_selfconsistency-{args.consistency}_" if args.consistency > 1 else ""

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

    args.max_tokens = 3996 if args.engine == 'chatgpt' else 8192  
    args.instructions = PROMPT_INSTRUCTION

    message = f"Generating responses for {args.engine} model"
    message += " with self-consistency" if args.consistency > 1 else " without self-consistency"
    logger.info(message)
    generator = Generator(args)

    # Load all the data from the input file
    all_questions = load_json_file(args.data_file_path)

    # Filter questions we already generated results for
    if os.path.exists(args.output_file_path):
        with open(args.output_file_path) as f:
            done_responses = json.load(f)
            done_responses = [d for d in done_responses if d["model.name"] == generator_models[args.engine]]

        if len(all_questions) != len(done_responses):
            done_questions = [q["question_id"] for q in done_responses]
            all_questions = [q for q in all_questions if q["question_id"] not in done_questions]
        else:
            logger.info(f"Already fully done!")
            return
    else: 
        done_responses = []

    logger.info(f"Total {len(all_questions)} questions to be processed\n")
    output_responses = []

    questions_by_course = {}

    for q in all_questions:
        course_id = q['course_id']
        if course_id not in questions_by_course:
            questions_by_course[course_id] = []
        questions_by_course[course_id].append(q)

    for i, c_id in enumerate(questions_by_course):
        t1 = time.time()
        questions = questions_by_course[c_id]
        logger.info(f"Generating responses for {c_id} ... ({i}/{len(questions)})")
        args.course_id = c_id

        queries = []
        for question in questions:
            question['prompt_language'] = args.prompt_language
            if args.shots > 0:
                # Sample and add demonstrations
                examples_list = sample_demonstration(args, question)
                query = {"problem": question, "examples": examples_list}
            else:
                query = {"problem": question}
            queries.append(query)

        output_responses = generator.batch_generate(queries)
        done_responses += output_responses
        
        with open(args.output_file_path, "w") as f:
            json.dump(done_responses, f, indent=2, ensure_ascii=False)

        logger.info(f"{len(queries)} question processed in {time.time() - t1} seconds")
        print("************************************************************")

    with open(args.output_file_path, "w") as f:
            json.dump(done_responses, f, indent=2, ensure_ascii=False)

    failed_questions_file = args.output_file_path.replace(".json", "_failed.json")
    with open(failed_questions_file, "a+") as f:
        json.dump(generator.failed_examples, f, indent=2, ensure_ascii=False)

    logger.info(f"{all_questions} question processed in {time.time() - t1} seconds")
    print("************************************************************")


if __name__ == "__main__":
    main()
