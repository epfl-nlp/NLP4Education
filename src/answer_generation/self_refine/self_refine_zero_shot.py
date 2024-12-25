import logging
import argparse
import os
import pandas as pd
import time
import json

from tqdm import tqdm
import openai
from torch.utils.data import DataLoader

from prompt_utils import get_system_message, create_question_content

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
    """ Loads json file """
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
        raise NotImplementedError("Completion mode is not supported for the self-refine method.")

    def chat(self, prompt):
        messages = []

        sys_message = get_system_message(prompt["problem"])
        messages.append(sys_message)
        if "examples" in prompt:
            for example in prompt["examples"]:
                raise NotImplementedError("few-shot is currently not supported.")

        # Get the prompt
        question_content = create_question_content(prompt["problem"])
        messages.append({"role": "user", "content": question_content})

        flag = True
        while flag:  # while getting exception from API, retry
            try:
                response = openai.ChatCompletion.create(model=self.model,
                                                        messages=messages,
                                                        top_p=1.0,
                                                        temperature=0.8,
                                                        frequency_penalty=0.8,
                                                        presence_penalty=0.5,
                                                        )
                flag = False
            except Exception as e:
                logger.info(f"The following error has happened. Waiting for 5seconds:\n{e}")
                time.sleep(5)
        output_text = response["choices"][0]["message"]["content"]

        output = {"question_id": prompt["problem"]["question_id"],
                  "model_output": output_text,
                  "prompt_type": self.args.prompt_type,
                  "prompt_text": messages,
                  "model": {"name": self.model},
                  }
        return output


    def postprocess(self, output, record):
        raise NotImplementedError

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
            except Exception as e:
                self.failed_examples.append(query)
                course_id = query["problem"]["course_id"]
                logger.info(f"Error in generating response for {query} in course {course_id} due to {e}")
                continue

        return batch_generation_outputs


def parse_args():
    parser = argparse.ArgumentParser(description="Performing self-refine for the input dataset (zero-shot mode).")
    parser.add_argument("--gen_mode", type=str, default="chat")
    parser.add_argument("--engine", type=str, default="chatgpt")
    parser.add_argument("--prompt_type", type=str, default="0-shot",
                        help="prompt type in the format of '{k}-shot', like '0-shot'.")
    parser.add_argument("--data_file_path", type=str, help="path to input json containing (latest) valid question/answers.",  required=True)
    parser.add_argument("--output_file_path", type=str, help='Output file path', required=True)
    parser.add_argument("--courses_info_file_path", type=str, help='Courses information file path', required=True)
    parser.add_argument("--target_course_id", type=str, default="ALL",
                        help="either the target course id or 'ALL'")
    parser.add_argument("--target_question_type", type=str, default="mcq",
                        help="either 'mcq' (multi-choice) or 'oe' (open-ended)")
    parser.add_argument("--api_key", type=str, default="", required=True)
    parser.add_argument("--organization", type=str, default="", required=True)
    args = parser.parse_args()

    if args.target_question_type == "mcq":
        logger.info(f"Targeting multiple-choice questions in {args.target_course_id} course(s).")
    elif args.target_question_type == "oe":
        raise NotImplementedError("Open ended questions are currently not supported for self-refine method.")
    else:
        raise ValueError("Only 'oe' or 'mcq' can be passed for the 'target_question_type'.")

    if args.prompt_type != '0-shot':
        raise NotImplementedError("Currently only zero-shot is supported for self-refine.")

    return args


def get_input_dataset(args):
    """ Load the input dataset and filter out the questions based on the target course_id and question_type """
    input_dataset = pd.read_json(args.data_file_path)
    logger.info(f"Starting from {input_dataset.shape[0]} questions in the input dataset...")
    input_dataset = input_dataset[input_dataset.question_type == args.target_question_type].reset_index(drop=True)
    logger.info(f"{input_dataset.shape[0]} questions of type {args.target_question_type} in the input dataset...")
    if args.target_course_id != "ALL":
        input_dataset = input_dataset[input_dataset.course_id == int(args.target_course_id)].reset_index(drop=True)
    logger.info(f"{input_dataset.shape[0]} questions after keeping {args.target_course_id} course(s).")

    if args.target_question_type == "mcq":
        # removing invalid questions
        input_dataset = input_dataset[input_dataset.question_options.apply(lambda x: x != [])].reset_index(drop=True)
    logger.info(f"{input_dataset.shape[0]} questions after filtering out  invalid questions.")

    return input_dataset


def main():
    args = parse_args()

    openai.api_key = args.api_key
    openai.organization = args.organization

    # Read courses information
    courses_info_list = load_json_file(args.courses_info_file_path)
    courses_info = {}

    for c in courses_info_list:
        courses_info[c["course_id"]] = c

    input_dataset = get_input_dataset(args)

    logger.info(f"Generating responses for {args.prompt_type} prompting and for {args.engine} model ...\n")
    generator = Generator(args)

    querys = []
    for _, q in input_dataset.iterrows():
        q["course_name"] = courses_info[q["course_id"]]["course_name"]
        query = {"problem": q, "examples": []}
        querys.append(query)

    output_responses = generator.batch_generate(querys)
    with open(args.output_file_path, "w") as f:
        json.dump(output_responses, f, indent=4)

    failed_questions_file = args.output_file_path.replace(".json", "_failed.json")
    with open(failed_questions_file, "a+") as f:
        json.dump(generator.failed_examples, f, indent=4)


if __name__ == "__main__":
    main()
