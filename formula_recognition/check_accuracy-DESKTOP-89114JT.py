import gpt_crawler
import time
import threading
from sympy import sympify, Eq
import os


DEFAULT_DRIVER = None
TIMEOUT = 600
error = 3

def main():
    global DEFAULT_DRIVER

    driver = gpt_crawler.connect_browser()
    DEFAULT_DRIVER = driver
    print('success to connect driver!')

    # If you don't know window handle informations, then you can use this function.
    #gpt_crawler.print_window_handles()

    first_msg = 'Read the mathematical expression and express it in LaTeX syntax. Solve the problem and output the answer at the end. The response must always end in the form of "In the LaTeX syntax, the expression is ~~~. The Answer is ~~~."'
    origin_first_msg = '''The given image is a mathematical expression. Your task is to correctly interpret this mathematical expression and do your best to solve the problem.

I want the following three things:
- The mathematical expression represented in LaTeX syntax as written in the image.
- The exact solution.
- An approximate value.

Please provide these values to me at the end of your response in the following format:
#problem: \sum_{x=1}^{10} 2^{- 8 x}
#solution: 12093235/60466176
#evalf_value: 0.199999996692366'''
    augmentation_first_msg = '''The given image is a mathematical expression. Your task is to correctly interpret this mathematical expression and do your best to solve the problem. The red gridlines are there to help you better understand the positioning of the mathematical expression in the image. These red lines are drawn vertically or horizontally across the picture.

I want the following three things:
- The mathematical expression represented in LaTeX syntax as written in the image.
- The exact solution.
- An approximate value.

Please provide these values to me at the end of your response in the following format:
#problem: \sum_{x=1}^{10} 2^{- 8 x}
#solution: 12093235/60466176
#evalf_value: 0.199999996692366'''
    # laptop version
    first_image_format = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\Lecture\2023-2\2023-2 Natural Language Processing (001)\project\LLM_Babysitting_Project\formula_recognition\data\random_problems_v1\problem{}.png"
    # desktop version
    first_image_format = r"C:\Users\LeeYuseop\OneDrive\바탕 화면\Lecture\2023-2\2023-2 Natural Language Processing (001)\project\LLM_Babysitting_Project\formula_recognition\data\random_problems_v2\problem{}.png"

    file_path_format = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\Lecture\2023-2\2023-2 Natural Language Processing (001)\project\LLM_Babysitting_Project\formula_recognition\data\random_problems_v1\problem{}_gpt_latex_respond.txt"
    # desktop version
    file_path_format = r"C:\Users\LeeYuseop\OneDrive\바탕 화면\Lecture\2023-2\2023-2 Natural Language Processing (001)\project\LLM_Babysitting_Project\formula_recognition\data\random_problems_v2\problem{}_gpt_latex_respond+.txt"
    #window_handle = "A33BD7DE9DE8F8385BAE5D10573AF601"  # notebook NLP
    window_handle = "67D07B4A6D6B58CFF6734297AD006D9C"      # desktop NLP
    model = "gpt-4"

    # 52번부터 형식에 맞게 출력 됨 (first_msg 수정)

    base_path = 'C:/Users/SAMSUNG/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/'
    base_path = 'C:/Users/LeeYuseop/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/'
    origin_image_format = base_path + "formula_recognition/data/random_problems_v2/problem{}.png"
    augmentation_image_format = base_path + "formula_recognition/data/random_problems_v2/problem{}_{}_{}.png"
    file_path_format = "./formula_recognition/data/random_problems_v2/problem{}_{}_{}.txt"

    print('Ready!')

    # 1 1 7 #problem 이상하게 되어 있음
    next_i = 1
    next_r = 3
    next_c = 4
    wait_time=180
    for i in range (1, 101):
        if i < next_i: continue

        for r in range(1, 11):
            if i == next_i and r < next_r: continue

            for c in range(1, 11):
                if i == next_i and r == next_r and c < next_c: continue

                if r == 1 and c == 1:
                    first_image = origin_image_format.format(i)
                    first_msg = origin_first_msg
                else:
                    first_image = augmentation_image_format.format(i, r, c)
                    first_msg = augmentation_first_msg
                file_path = file_path_format.format(i, r, c)
                #first_image = first_image_format.format(i)
                #first_image = None
                #file_path = file_path_format.format(i)

                flag = True
                cnt = 0
                while flag and cnt < 5:
                    cnt = cnt + 1
                    try:
                        flag = False
                        wait_time = max(wait_time, 10)
                        print('----------------------------------------------------------------------------------------')
                        print('#', i, r, c, wait_time)
                    

                        agent = gpt_crawler.start_new_chat(driver=driver, first_msg=first_msg, first_image=first_image, window_handle=window_handle, model=model, wait_time=wait_time)
                        time.sleep(1)

                        gpt_respond = agent['conversations'][1]
                        print(gpt_respond)

                        with open(file_path, 'w', encoding='utf-8') as file:
                            file.write(gpt_respond)

                        '''gpt_respond_split = gpt_respond.split('\n')
                        if len(gpt_respond_split) == 1 or gpt_respond_split[0] != 'ChatGPT':
                            flag = True

                        if gpt_respond_split[-1] == 'Our systems have detected unusual activity from your system. Please try again later.':
                            time.sleep(180)'''
                        
                        # 'ChatGPT', '#problem \', '#evalf_value'가 모두 있으면 성공
                        if 'ChatGPT' in gpt_respond and '#problem' in gpt_respond and '#evalf_value' in gpt_respond:
                            wait_time = wait_time - 10
                        else:
                            wait_time = wait_time + 10
                            flag = True
                        
                        time.sleep(3)

                    except Exception as e:
                        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                        print(e)
                        flag = True
                        wait_time = wait_time + 10
                        time.sleep(3)

                    for _ in range(5):
                        try:
                            gpt_crawler.delete_agent(driver=driver, window_handle=window_handle, agent=agent)
                            time.sleep(1)
                            break

                        except Exception as e:
                            print('///////////////////////////////////////////////////////////////')
                            print('delete error')
                            time.sleep(3)

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
            gpt_crawler.start_new_chat(driver=driver, agent=agent, first_images=question_images, first_msg=question_text, window_handle=window_handle, model=model)

            with open(answer_path, 'w', encoding='utf-8') as file:
                file.write(agent['conversations'][-1])
            
            gpt_crawler.delete_agent(driver=driver, agent=agent)
        
        result = evaluate_task(answer_path, solution_path)

        print(task_id, "'s result:", result)
        
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



def check_accuracy(driver=None, window_handles=None, tasks=None, model='gpt-4'):
    agents = []
    for window_handle in window_handles:
        agents.append(gpt_crawler.set_agent(model=model, window_handle=window_handle, status=gpt_crawler.AgentStatus.FREE))

    for task in tasks:
        # wait until there exists a free agent
        '''while True:
            agent = find_free_agent(agents=agents)
            if agent is not None: break
            time.sleep(1)'''
        agent = agents[0]
        
        thread = threading.Thread(target=do_task, args=(driver, agent, task))
        thread.start()
        thread.join(timeout=TIMEOUT)

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
        '0AEEF1D4383684F59D431FBDA460D052'
    ]
    window_handles = [      # desktop
        '5E4B705AE092E8B3B3F1880ABFA82350'
    ]

    base_path = 'C:/Users/SAMSUNG/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/formula_recognition/data/random_problems_v3/'
    base_path = 'C:/Users/LeeYuseop/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/formula_recognition/data/random_problems_v3/'
    tasks = make_tasks(base_path=base_path)


    check_accuracy(driver=driver, window_handles=window_handles, tasks=tasks, model='gpt-4')

    #main()