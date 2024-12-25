# Source Code README

[![License: CC-BY](https://img.shields.io/badge/License-CC--BY-blue.svg)](https://creativecommons.org/licenses/by/4.0/)


This folder contains the source code for implementing the six prompting strategies evaluated in this study. Each sub-folder is dedicated to a specific prompting strategy, accompanied by a detailed `README.md` for further guidance.
## Directory Structure

```plaintext
    src/
    │
    ├── answer_generation/    # Source code for different prompting strategies
    │   ├── chain_of_thought/       # Chain-of-Thought (CoT) Prompting
    │   ├── expert_prompting/      # Expert Prompting
    │   └── few_shot_prompting/     # Few-shot Prompting
    │   └── metacognitive/     # Metacognitive prompting
    │   └── self_refine/     # Self-refine Prompting
    │   └── tree_of_thought/     # Tree-of-Though (ToT) Prompting
    │
    ├── grading/
        ├── grade_open_answer.py.py  # Direct grading of open-ended questions
        └── README.md # Documentation