# Last updated: 2023. 11. 28. 15:57

import gpt_crawler
import time
import threading
from sympy import sympify, Eq
import os


DEFAULT_DRIVER = None
TIMEOUT = 600
LOCK = threading.Lock()
error = 3



def find_free_agent(agents=[]):
    for agent in agents:
        if agent['status'] == gpt_crawler.AgentStatus.FREE:
            return agent
    
    return None


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def get_problem_expr(context):
    for line in context:
        if '#problem: ' in line:
            expr_text = line[len('#problem'):]
            expr = sympify(expr_text)

            return expr
    
    return None


def evaluate_task(answer_path, solution_path):
    answer = read_file(answer_path)
    solution = read_file(solution_path)

    answer_problem_expr = get_problem_expr(answer)
    solution_problem_expr = get_problem_expr(solution)

    if answer_problem_expr is None: return False
    if Eq(answer_problem_expr, solution_problem_expr): return True


def is_it_done(answer_path):
    if not os.path.exists(answer_path): return False

    with open(answer_path, 'r', encoding='utf-8') as file:
        text = file.read()

    if 'ChatGPT' not in text: return False
    if '#problem: \\' not in text: return False
    if '#evalf_value' not in text: return False

    return True


def do_task(driver, agent, task):
    agent['lock'].acquire()

    try:
        task_id = task['task_id']
        question = task['question']
        answer_path = task['answer_path']
        solution_path = task['solution_path']

        question_images = question['images']
        question_text = question['text']

        window_handle = agent['window_handle']
        model = agent['model']

        if is_it_done(answer_path):
            print('Already Done', task_id)
        else:
            print('Start', task_id)
            time.sleep(1)
            gpt_crawler.start_new_chat(driver=driver, agent=agent, first_images=question_images, first_msg=question_text, window_handle=window_handle, model=model, lock=agent['lock'])

            with open(answer_path, 'w', encoding='utf-8') as file:
                file.write(agent['conversations'][-1])
            
            gpt_crawler.delete_agent(driver=driver, agent=agent)
            
            result = evaluate_task(answer_path, solution_path)

            print(task_id, "'s result:", result)

        agent['status'] = gpt_crawler.AgentStatus.FREE
        
    except Exception as e:
        global error
        error = error + 1
        error_path = f'./error/error{error}.txt'

        with open(error_path, 'w', encoding='utf-8') as file:
            file.write('Error Message:\n')
            file.write(str(e))
            file.write('\n\n')
            file.write('Page Source:\n')
            file.write(driver.page_source)
    
    agent['lock'].release()



def check_accuracy(driver=None, window_handles=None, tasks=None, model='gpt-4'):
    agents = []
    for window_handle in window_handles:
        agents.append(gpt_crawler.set_agent(model=model, window_handle=window_handle, status=gpt_crawler.AgentStatus.FREE, lock=LOCK))

    for task in tasks:
        # wait until there exists a free agent
        while True:
            agent = find_free_agent(agents=agents)
            if agent is not None: break
            time.sleep(1)
        agent['status'] = gpt_crawler.AgentStatus.NOT_STARTED
        #agent = agents[0]
        
        thread = threading.Thread(target=do_task, args=(driver, agent, task))
        thread.start()
        #thread.join(timeout=TIMEOUT)

        '''if thread.is_alive():
            # 'Thread' object has no attribute 'terminate'
            thread.terminate()
            print('Timeout Error')'''


def make_tasks(base_path=None):
    original_first_msg = '''The given image is a mathematical expression. Your task is to correctly interpret this mathematical expression and do your best to solve the problem.

I want the following three things:
- The mathematical expression represented in LaTeX syntax as written in the image.
- The exact solution.
- An approximate value.

Please provide these values to me at the end of your response in the following format:
#problem: \sum_{x=1}^{10} 2^{- 8 x}
#solution: 12093235/60466176
#evalf_value: 0.199999996692366'''

    augmentation_first_msg = '''The given images are mathematical expressions. One is the original image, and the other is the image with red gridlines added to the original image. The red gridlines help you better understand the positioning of the mathematical expression in the image. These red lines are drawn vertically or horizontally across the picture. Your task is to correctly interpret this mathematical expression and do your best to solve the problem.

I want the following three things:
- The mathematical expression represented in LaTeX syntax as written in the image.
- The exact solution.
- An approximate value.

Please provide these values to me at the end of your response in the following format:
#problem: \sum_{x=1}^{10} 2^{- 8 x}
#solution: 12093235/60466176
#evalf_value: 0.199999996692366'''

    if base_path is None:
        base_path = 'C:/Users/SAMSUNG/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/formula_recognition/data/random_problems_v3/'

    tasks = []
    for i in range(8, 31):
        for j in range(1, 4):
            task = {}

            task['task_id'] = f'problem{i}_1_1_{j}'

            images = [
                base_path + f'problem{i}.png'
            ]

            question = {
                'images': images,
                'text': original_first_msg
            }
            task['question'] = question

            task['answer_path'] = base_path + f'answer{i}_1_1_{j}.txt'
            task['solution_path'] = base_path + f'problem{i}.txt'

            tasks.append(task)

    for i in range(1, 31):
        for r in range(1, 11):
            for c in range(1, 11):
                if r == 1 and c == 1: continue

                for j in range(1, 4):
                    task = {}

                    task['task_id'] = f'problem{i}_{r}_{c}_{j}'

                    images = [
                        base_path + f'problem{i}.png',
                        base_path + f'problem{i}_{r}_{c}.png'
                    ]

                    question = {
                        'images': images,
                        'text': augmentation_first_msg
                    }
                    task['question'] = question

                    task['answer_path'] = base_path + f'answer{i}_{r}_{c}_{j}.txt'
                    task['solution_path'] = base_path + f'problem{i}.txt'

                    tasks.append(task)

    
    return tasks



if __name__ == "__main__":
    # If you wankt to use it, then check belows:
    # - window_handles
    # - base_path
    # - make_tasks function (if you change task question or images form)
    # - do_task function (if you change task question form)
    # - is_it_done function (if you chagne task quesion or images form)

    driver = gpt_crawler.connect_browser()

    # If you don't know window handle informations, then you can use this function.
    #gpt_crawler.print_window_handles()

    window_handles = [      # notebook
        '0A0192CF600F9F4CC207421DB14F7BAE'
    ]
    window_handles = [      # desktop
        '8FF148CBAFBBB168BD573568D7C39B20',
        'C0D429F852CCF06514854235127895CE',
        '9ABA812D57301412FC6998D368524FF8',
        'E448CE37FAEF7D43D88B7A54BF4D0569',
        'F3FD5948DA105408DCE669FD8595BCD8'
    ]
    '''window_handles = [
        '8FF148CBAFBBB168BD573568D7C39B20'
    ]'''

    base_path = 'C:/Users/SAMSUNG/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/formula_recognition/data/random_problems_v3/'
    base_path = 'C:/Users/LeeYuseop/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/formula_recognition/data/random_problems_v3/'
    tasks = make_tasks(base_path=base_path)


    check_accuracy(driver=driver, window_handles=window_handles, tasks=tasks, model='gpt-4')

    #main()