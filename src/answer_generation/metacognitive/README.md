# Meta Cognitive Prompting
Metacognitive paper: [here](https://arxiv.org/pdf/2308.05342.pdf)

## Usage

This prompting strategy can be run using `metacognitive.py` with the following arguments:

- **engine**: chatgpt or gpt-4 (required)
- **api_key**: OpenAI API key (required)
- **organization**: OpenAI organization (required)
- **data_file_path**: JSON file path of questions (required)
- **output_file_path**: JSON file path to save the results (required)
- **course_info_file_path**: JSON file path of course metadata (required)
- **prompt_language**: Language of the prompt text [english, french, inverted] (default value is english) 
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
python metacognitive.py \
    --engine chatgpt \ 
    --max_tokens 1024 \
    --temperature 0.8 \ 
    --top_p 1.0 \
    --frequency_penalty 0.8 \
    --presence_penalty 0.5 \
    --data_file_path questions.json \
    --output_file_path metacognitive.json \
    --api_key OPENAI_API_KEY \
    --organization OPENAI_ORGANIZATION \
    --prompt_language english \
    --course_info_file_path courses.json \
```
