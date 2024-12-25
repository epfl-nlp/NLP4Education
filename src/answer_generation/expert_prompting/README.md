# Expert Prompting

We ask the model to identify experts `E` in the field, generate answers as if the experts wrote them, and combine the experts’ answers by collaborative decision-making (majority voting). 

## Usage: Generating Answers

Generating the results for this strategy can be done in two steps:

- **Step 1:** For each question, we ask the model to output the name of three experts capable of solving the question. The output of this step is a JSON file of all questions information plus a new filed called `raw-experts` that is a list of expert names.
- **Step 2:** We use each expert name generated in step 1 as the system message, and ask the model to solve the question. In the ouput file, the `model_output` is a list of string.

This prompting strategy can be run using `expert_prompting.py` with the following arguments:

- **engine**: chatgpt or gpt-4 (required)
- **api_key**: OpenAI API key (required)
- **organization**: OpenAI organization (required)
- **data_file_path**: JSON file path of questions for step-1 and JSON file path of question including the name of the experts in step-2 (required)
- **output_file_path**: JSON file path to save the results (required)
- **prompt_step**: step-1 or step-2 (default value is step-1)
- **max_tokens**: The maximum number of tokens to generate (default value is None)
- **temperature**: Sampling temperature $\in [0,1]$ (default value is 0.8)
- **presence_penalty**: Presence penalty $\in [-2,2]$ (default value is 0.5)
- **frequency_penalty**: Frequency Penalty $\in [-2,2]$ (default value is 0.8)
- **data_file_path**: Questions file path (required)
- **courses_info_file_path**: Course information file path (required)
- **output_file_path**: Output file path to save generated answers (required)
- **api_key**: OpenAI API key (required)
- **organization**: OpenAI organization (required)

```
python expert_prompting.py \
    --engine chatgpt \ 
    --max_tokens 1024 \
    --temperature 0.8 \ 
    --top_p 1.0 \
    --frequency_penalty 0.8 \
    --presence_penalty 0.5 \
    --data_file_path questions.json \
    --course_info_file_path courses.json \
    --output_file_path expert_prompting_step_1.json \
    --api_key OPENAI_API_KEY \
    --organization OPENAI_ORGANIZATION \
    --prompt_step step-1 

```

## Usage: Majority Voting

- **open_answer questions**: We ask the model to detect the best answer among the three generated answers from the previous step.
```
python majority_voting.py \
    --engine chatgpt \ 
    --max_tokens 1024 \
    --temperature 0.8 \ 
    --top_p 1.0 \
    --frequency_penalty 0.8 \
    --presence_penalty 0.5 \
    --data_file_path questions.json \
    --output_file_path majority_voting.json \
    --api_key OPENAI_API_KEY \
    --organization OPENAI_ORGANIZATION \

```
