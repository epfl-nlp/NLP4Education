# Tree of Thought Prompting
Tree of Thought Prompting Paper: [here](https://arxiv.org/abs/2305.10601)


## Usage
This prompting strategy can be run using `tot_prompting.py` with the following arguments:

- **engine**: chatgpt or gpt-4 (required)
- **api_key**: OpenAI API key (required)
- **organization**: OpenAI organization (required)
- **data_file_path**: JSON file path of questions (required)
- **output_file_path**: JSON file path to save the results (required)
- **max_tokens**: The maximum number of tokens to generate (default value is None)
- **temperature**: Sampling temperature $\in [0,1]$ (default value is 0.8)
- **presence_penalty**: Presence penalty $\in [-2,2]$ (default value is 0.5)
- **frequency_penalty**: Frequency Penalty $\in [-2,2]$ (default value is 0.8)
- **prompt_type**: Prompt type (default value is `tree_of_thought`)
- **data_file_path**: Questions file path (required)
- **courses_info_file_path**: Course information file path (required)
- **output_file_path**: Output file path to save generated answers (required)
- **api_key**: OpenAI API key (required)
- **organization**: OpenAI organization (required)


```
python tot_prompting.py \
    --engine chatgpt \ 
    --max_tokens 1024 \
    --temperature 0.8 \ 
    --top_p 1.0 \
    --frequency_penalty 0.8 \
    --presence_penalty 0.5 \
    --data_file_path questions.json \
    --courses_info_file_path courses.json \
    --output_file_path tot_prompting.json \
    --api_key OPENAI_API_KEY \
    --organization OPENAI_ORGANIZATION \
```