
# Could ChatGPT get an Engineering Degree? Evaluating Higher Education Vulnerability to AI Assistants.

[![License: CC BY-NC-ND](https://img.shields.io/badge/License-CC%20BY--NC--ND-blue.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)
[![License: CC-BY](https://img.shields.io/badge/License-CC--BY-blue.svg)](https://creativecommons.org/licenses/by/4.0/)

This repository provides the dataset and source code used in the study: "[Could ChatGPT get an Engineering Degree? Evaluating Higher Education Vulnerability to AI Assistants.](https://www.pnas.org/doi/10.1073/pnas.24149551212)" [PNAS 2024]
- The dataset is located in the `data` folder and includes:
    - `questions.json`: Contains all the questions (and their answers) used in this study.
    - `course.json`: Provides information about the courses analyzed in this work.
    - `grade_per_question.csv`: Contains models' grades (`gpt-3.5-turbo` and `gpt-4`) for all questions across six different prompting strategies.
    - `README.md`: Readme file for more details on the data format.
- The source code is located in the `src` folder. Each subfolder contains dedicated README files for further details. Key components include:

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
    
   
## Licenses:
- The dataset is released under [CC-BY-NC-ND](https://creativecommons.org/licenses/by-nc-nd/4.0/deed.en) license. 
- The code is released under [CC-BY](https://creativecommons.org/licenses/by/4.0/) license.  

## Citation
If you use this code for your research, please cite our paper:

``` bib
@article{doi:10.1073/pnas.2414955121,
    author = {Beatriz Borges and Negar Foroutan and Deniz Bayazit and Anna Sotnikova and Syrielle Montariol  and Tanya Nazaretzky  and Mohammadreza Banaei  and Alireza Sakhaeirad  and Philippe Servant  and Seyed Parsa Neshaei and Jibril Frej and Angelika Romanou  and Gail Weiss  and Sepideh Mamooler  and Zeming Chen  and Simin Fan  and Silin Gao  and Mete Ismayilzada  and Debjit Paul  and Philippe Schwaller  and Sacha Friedli  and Patrick Jermann  and Tanja Käser  and Antoine Bosselut  and EPFL Grader Consortium and EPFL Data Consortium},
    title = {Could ChatGPT get an engineering degree? Evaluating higher education vulnerability to AI assistants},
    journal = {Proceedings of the National Academy of Sciences},
    volume = {121},
    number = {49},
    pages = {e2414955121},
    year = {2024},
    doi = {10.1073/pnas.2414955121},
    URL = {https://www.pnas.org/doi/abs/10.1073/pnas.2414955121},
    eprint = {https://www.pnas.org/doi/pdf/10.1073/pnas.2414955121}
}
```