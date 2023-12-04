# Last updated: 2023. 11. 28. 15:57

import gpt_crawler
import time
import threading
import sympy as sp
from sympy import sympify, Eq
import os
import sys

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


def convert_text2expr(text):
    text = text.replace('\sum_{x=1}^{10}', '')
    text = text.replace(' ', '')
    text = text.replace(r'\left', '')
    text = text.replace(r'\right', '')

    return text

def get_problem_expr(text):
    for line in text.split('\n'):
        if '#problem: ' in line:
            expr_text = line[len(r'#problem: \sum_{x=1}^{10} '):]
            #print(expr_text)

            expr = convert_text2expr(expr_text)
            #print(expr)

            return expr

    return None

def get_evalf_value(text):
    for line in text.split('\n'):
        if '#evalf_value: ' in line or '#evalf_avlue: ' in line:
            evalf_str = line.split(':')[-1]
            if evalf_str[-1] == '.': evalf_str = evalf_str[:-1]

            evalf_value = float(evalf_str)

            return evalf_value

    return None


def evaluate_task(answer_path, solution_path):
    #print('-----------------------------------------------------------------------------')
    answer = read_file(answer_path)
    solution = read_file(solution_path)

    '''#print('# answer:')
    answer_problem_expr = get_problem_expr(answer)
    #print('# solution:')
    solution_problem_expr = get_problem_expr(solution)

    if answer_problem_expr is None: return False
    #if Eq(answer_problem_expr, solution_problem_expr): return True
    if answer_problem_expr == solution_problem_expr: return True'''

    answer_evalf_value = get_evalf_value(answer)
    solution_evalf_value = get_evalf_value(solution)

    #print(answer_evalf_value)
    #print(solution_evalf_value)

    if answer_evalf_value is None or solution_evalf_value is None:
        return False

    ERROR = 0.000001
    if abs(answer_evalf_value - solution_evalf_value) <= ERROR:
        return True
    else:
        return False


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

        print(e)
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
    for i in range(1, 31):
        if i == 1 or i == 11 or i == 23: continue
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

    for i in range(2, 31):
        if i == 1 or i == 11 or i == 23: continue
        for r in range(1, 11):
            for c in range(1, 11):
                if r == 1 and c == 1: continue
                if r != c and c > 1: continue

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

    for i in range(2, 31):
        if i == 1 or i == 11 or i == 23: continue
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


def print_accuracy():
    base_path = 'C:/Users/SAMSUNG/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/formula_recognition/data/random_problems_v3/'
    result_path = './formula_recognition/data/random_problem_v3_result.txt'

    results = [[[[None for _ in range(4)] for _ in range(11)] for _ in range(11)] for _ in range(31)]
    for i in range(1, 31):
        for r in range(1, 11):
            for c in range(1, 11):
                for j in range(1, 4):
                    answer_path = base_path + f'answer{i}_{r}_{c}_{j}.txt'
                    solution_path = base_path + f'problem{i}.txt'

                    try:
                        results[i][r][c][j] = evaluate_task(answer_path=answer_path, solution_path=solution_path)

                    except Exception as e:
                        #print(f'{i} {r} {c} {j}:', e)
                        True


    with open(result_path, 'w', encoding='utf-8') as file:
        print('# Original image accuracy')
        file.write('# Original image accuracy\n')

        total_sum = 0
        total_cnt = 0

        for i in range(1, 31):
            #print(f'{i:2d}:', end='\t')
            file.write(f'{i:2d}:\t')

            sum = 0
            cnt = 0
            for j in range(1, 4):
                answer_path = base_path + f'answer{i}_1_1_{j}.txt'
                solution_path = base_path + f'problem{i}.txt'

                try:
                    result = evaluate_task(answer_path=answer_path, solution_path=solution_path)
                    #print(result, end='\t')
                    file.write(str('1' if result else '0') + '\t')

                    if result: sum += 1
                    cnt += 1

                except Exception as e:
                    #print()
                    print(f'{i} {j}:', e)
                    file.write('-\t')

            if cnt == 0:
                #print('-%')
                file.write('-%\n')
            else:
                #print(f'{sum/cnt*100:.2f}%')
                file.write(f'{sum/cnt*100:.2f}%\n')

            total_sum += sum
            total_cnt += cnt
        
        #print(f'total_accuray: {total_sum/total_cnt*100:.2f}%')
        #print()
        if total_cnt == 0:
            file.wirte('total_accuracy: -%\n')
        else:
            file.write(f'total_accuracy: {total_sum/total_cnt*100:.2f}%\n')
        file.write(f'total_sum: {total_sum}\n')
        file.write(f'total_cnt: {total_cnt}\n')
        file.write('\n')

        
        print('# Augmentation image accuracy - problem#')
        file.write('# Augmentation image accuracy - problem#\n')

        total_sum = 0
        total_cnt = 0
        for i in range(1, 31):
            #print(f'{i:2d}:', end='\t')
            file.write(f'{i:2d}:\t')

            problem_sum = 0
            problem_cnt = 0
            for r in range(1, 11):
                for c in range(1, 11):
                    sum = 0
                    cnt = 0
                    for j in range(1, 4):
                        answer_path = base_path + f'answer{i}_{r}_{c}_{j}.txt'
                        solution_path = base_path + f'problem{i}.txt'

                        try:
                            result = evaluate_task(answer_path=answer_path, solution_path=solution_path)
                            #print(result, end='\t')
                            #file.write(str('1' if result else '0') + '\t')

                            if result: sum += 1
                            cnt += 1

                        except Exception as e:
                            #print()
                            print(f'{i} {r} {c} {j}:', e)
                            #file.write('-\t')

                    if cnt == 0:
                        #print('-%')
                        file.write('-%\t')
                    else:
                        #print(f'{sum/cnt*100:.2f}%')
                        file.write(f'{sum/cnt*100:.2f}%\t')
                    
                    problem_sum += sum
                    problem_cnt += cnt

            if problem_cnt == 0:
                file.write(f'-%\t{problem_sum}\t{problem_cnt}\n')
            else:
                file.write(f'{problem_sum/problem_cnt*100:.2f}%\t{problem_sum}\t{problem_cnt}\n')

            total_sum += problem_sum
            total_cnt += problem_cnt

        
        if total_cnt == 0:
            file.wirte('total_accuracy: -%\n')
        else:
            file.write(f'total_accuracy: {total_sum/total_cnt*100:.2f}%\n')
        file.write(f'total_sum: {total_sum}\n')
        file.write(f'total_cnt: {total_cnt}\n')

        
        '''print('# Augmentation image accuracy - r by c')
        file.write('# Augmentation image accuracy - r by c\n')

        total_sum = 0
        total_cnt = 0
        for r in range(1, 11):
            for c in range(1, 11):

                
                sum = 0
                cnt = 0
                for i in range(1, 31):
                    for j in range(1, 4):
                        answer_path = base_path + f'answer{i}_{r}_{c}_{j}.txt'
                        solution_path = base_path + f'problem{i}.txt'

                        try:
                            result = evaluate_task(answer_path=answer_path, solution_path=solution_path)
                            #print(result, end='\t')
                            #file.write(str('1' if result else '0') + '\t')

                            if result: sum += 1
                            cnt += 1

                        except Exception as e:
                            #print()
                            print(f'{i} {r} {c} {j}:', e)
                            #file.write('-\t')

                    if cnt == 0:
                        #print('-%')
                        file.write('-%\t')
                    else:
                        #print(f'{sum/cnt*100:.2f}%')
                        file.write(f'{sum/cnt*100:.2f}%\t')
                    
                    prolbem_sum += sum
                    problem_cnt += cnt

            if problem_cnt == 0:
                file.write(f'-%\t{problem_sum}\t{problem_cnt}\n')
            else:
                file.write(f'{total_sum/total_cnt*100:.2f}%\t{problem_sum}\t{problem_cnt}\n')

            total_sum += problem_sum
            total_cnt += problem_cnt

        
        if total_cnt == 0:
            file.wirte('total_accuracy: -%\n')
        else:
            file.write(f'total_accuracy: {total_sum/total_cnt*100:.2f}%\n')
        file.write(f'total_sum: {total_sum}\n')
        file.write(f'total_cnt: {total_cnt}\n')'''


if __name__ == "__main__":
    print_accuracy()
    while True:
        True
    '''x = sp.symbols('x')

    str1 = r'(10 + x - 2x)'
    str2 = r'\sum_{x=1}^{10} \left(10 + x - 2 x\right)'
    print(str1)
    print(str2)

    expr1 = sympify(str1)
    expr2 = sympify(str2)

    result = expr1.equals(expr2)

    print(result)'''

    # If you wankt to use it, then check belows:
    # - window_handles
    # - base_path
    # - make_tasks function (if you change task question or images form)
    # - do_task function (if you change task question form)
    # - is_it_done function (if you chagne task quesion or images form)

    driver = gpt_crawler.connect_browser()

    # If you don't know window handle informations, then you can use this function.
    gpt_crawler.print_window_handles()

    window_handles = [      # notebook
        '0A0192CF600F9F4CC207421DB14F7BAE'
    ]
    window_handles = [      # desktop
        '8DD4EBE695E90A931BE6635919D9485D',
        '4CAC6A43B939DF56F1B5851A5EF5BA50',
        '7387FB8CAF1B7DFA0090ADA1DCD0EC95',
        'BB561CD39557B6FBA9A0C95A06146B91',
        'C75A61660C00B835E4C5716387D12A8E'
    ]
    '''window_handles = [
        '8FF148CBAFBBB168BD573568D7C39B20'
    ]'''

    base_path = 'C:/Users/SAMSUNG/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/formula_recognition/data/random_problems_v3/'
    base_path = 'C:/Users/LeeYuseop/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/formula_recognition/data/random_problems_v3/'
    tasks = make_tasks(base_path=base_path)


    check_accuracy(driver=driver, window_handles=window_handles, tasks=tasks, model='gpt-4')

    #main()