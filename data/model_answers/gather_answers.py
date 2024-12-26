import json

all_answers = []

for i in range(1, 7):
    answers = []
    path_name = f"model_answers_{i}.json"
    with open(path_name, "r") as f:
        answers = json.load(f)
    all_answers.extend(answers)
    print(path_name + " done.")
    
with open("model_answers.json", "w") as f:
    json.dump(all_answers, f, indent=4, ensure_ascii=False)

print("Answers gathered in model_answers.json")