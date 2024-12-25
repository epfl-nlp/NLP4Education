# Few-shot Prompting
## Usage

This prompting strategy can be run using `few_shot_prompting.py` with the following arguments:

- **engine**: chatgpt or gpt-4 (required)
- **api_key**: OpenAI API key (required)
- **organization**: OpenAI organization (required)
- **data_file_path**: JSON file path of questions (required)
- **output_file_path**: JSON file path to save the results (required)
- **prompt_type**: zero-shot or 1-shot (default value is zero-shot)
- **few_shot_folder**: Folder path to few-shots chosen for each question per course (required for 1-shot)
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
python few_shot_prompting.py \
    --engine chatgpt \ 
    --max_tokens 1024 \
    --temperature 0.8 \ 
    --top_p 1.0 \
    --frequency_penalty 0.8 \
    --presence_penalty 0.5 \
    --data_file_path questions.json \
    --output_file_path few_shot_prompting.json \
    --api_key OPENAI_API_KEY \
    --organization OPENAI_ORGANIZATION \
    --prompt_type 1-shot \
    --few_shot_folder few_shot_folder 

```
