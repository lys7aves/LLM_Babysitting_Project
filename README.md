# LLM Babysitting Project



## Outline
We are prompting team, so there are no training.
1. Image Prompting are nonverbal thus not in string. The code for lattice-prompting can be conducted with lattice_augmentor.py
2. Dataset can be found on data directory
3. Other codes are for GPT-4 crawling and generating data.
4. Multi-agent Prompting (TERA) can be found on SPP/prompts , written as  "role_prompt =  ..."
5. Multiagent Prompting (TERA) log can be found on SPP/logs

## Overview



## File Structure



```
LLM_Babysitting_Project
├── llm_babysitting (main folder)
│   ├── gpt_cralwer
│   	├── crawler.py
│   	└── agent.py
│   ├── tasks_generators
│   	├── sudoku_generator.py
│   	└── expression_generator.py
│   ├── data_augmentors
│   	├── lattice_augmentor.py
│   	└── mask_augmentor.py
│   ├── methods
│   	├── step_by_step_method.py
│   	├── lattice_method.py
│   	└── mask_metho.py
│   ├── data
│   ├── results
│   ├── experiment.py
│   ├── config.py
│   └── main.py
│
├── prev_data
├── docs
├── figs
├── results
├── setup.py
├── requirements.txt
└── README.md
```





