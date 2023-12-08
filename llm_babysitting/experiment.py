import gpt_crawler.crawler as Crawler
import gpt_crawler.agent as Agent
from gpt_crawler.agent import GptAgentState

import threading
import time
import os
import colorama
from colorama import Fore
import traceback

# experiment에 어떤 task를 어떤 method로 해볼지만 정하면 실험을 진행해주는 함수를 만드는게 개인적인 최종 목표

# data_generators 말고 task_generators를 만드는게 더 좋을거 같기도 하네요
# Before
#   /data_generators
#   /data_augmentors
# After
#   /task_generators > task와 solution 제작
#   /methos > task_generators에서 만든 task에 추가로 덧붙여서 task 제작 (data augment도 method에 맞게 augment)
#     ex, /methods/step_by_step_method.py > task에 "step by step" 만 덧붙여서 task 제작

# 큰 파이프라인인 experiment를 제작해주시면 제가 거기에 맞춰서 필요한 함수를 만들어도 될거 같기도 하고,
# 아래와 같은 파이프라인이라고 생각하고 task_generator나 method를 짜주셔도 될거 같아요.
# 프로젝트를 많이 진행해보지 않아서 설계가 엉성한데 의견 있으면 언제든 말씀해주시거나 반영해주셔도 될 것 같습니다.
# gpt_crawler를 안정적으로 만들어야 다른 모든게 될텐데.... 최대한 빨리 정확히 만들어보겠습니다

colorama.init()

def set_agents(lock):
    gpt4_tabs = [
        '6AE7FD505865F589CF21EB0815274ACD',
        '33C322877B760EF3C906A3A7505BCCAF',
        '0ECB85764F6D372DCED2E7D78EFCD6DA',
        '3504F117CCA00699331FE86D9F611DEF',
        'BECB5E9E8EBBEE562B4A72C22D78EC56'
    ]
    gpt3_tabs = [
        '1B4DF690BC13AB0DE7DE6BEC0CF47056',
        'A55BA2FEFE22D6D7A66B2F465165A6D3',
        '908A929A40B6355A0378D9124D068882',
        '7BACE35FE8FA29B4060B1C2F0D1A6AB8',
        'FF7A3BA01EB2D47ACDF0045DFD9C8B80'
    ]

    model = 'gpt-4'
    tabs = gpt4_tabs
    debug_mode = False
    num_agents = len(tabs)

    gpt_crawler = Crawler.GptCrawler(tabs=tabs, lock=lock, debug_mode=debug_mode)
    gpt_crawler.print_window_handles()

    agents = []
    for i in range(num_agents):
        agents.append(Agent.GptAgent(gpt_crawler=gpt_crawler, tab_index=i, model=model, name=str(i)))

    return agents



def run_task(lock=None, agent=None, message='', files=[], result_path=None, max_attempts=9999):
    agent.start(message=message, files=files)

    attempts = 0
    generate_error_cnt = 0
    generate_error_attempts = 0
    while attempts < max_attempts and agent.state != GptAgentState.AWAITING_INPUT:
        if agent.state == GptAgentState.ERROR_HANDLED:
            agent.close()
            time.sleep(1)
            agent.start(message=message, files=files)
        
        if agent.state == GptAgentState.REGENERATE_ERROR:
            generate_error_attempts += 1
            if generate_error_attempts == 100:
                generate_error_attempts = 0
                generate_error_cnt += 1
                if generate_error_cnt == 10:
                    break

                agent.close()
                time.sleep(1)
                agent.start(message = message, files=files)

        else:
            generate_error_attempts = 0

        attempts += 1
        time.sleep(1)
    
    if agent.state == GptAgentState.AWAITING_INPUT:
        if len(agent.conversations) == 0:
            print(Fore.RED)
            print('Error: There is no conversation')
            print(Fore.RESET)

        else:
            with open(result_path, 'w', encoding='utf-8') as file:
                file.write(agent.conversations[-1])

        agent.close()

    else:
        if lock is not None:
            lock.acquire()

        try:
            print(Fore.RED, end='')
            print('Error on do_task :(')
            print(str(agent))
            print(agent.state.name)
            print(agent.error_message)
            traceback.print_exc()
            print(Fore.RESET)

        finally:
            if lock is not None:
                lock.release()



def run_tasks(lock=None, agents=None, task_path=None, experiments_per_task=3):
    #tasks = os.listdir(task_path+'tasks/')
    file_base_path = 'C:/Users/LeeYuseop/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/llm_babysitting/data/task_1/'
    

    hws = [(5,5), (7,7), (6,6), (5,1), (1,5)]
    cnt = 0
    for h, w in hws:
        for i in range(2, 31):
            for j in range(1, 4):
                message = f"The two images are of the same expression. One is the original image, and the other has a lattice of {h} by {w} for precise location information.\n\nFirst, compare the two images, taking into account the accurate positioning, and read the expression correctly.\n\nThen, calculate the expression.\n\nPlease conclude your answer with 'The answer is ...' or 'The answer is approximately ...'.\n\nLet's think step by step."
                files = [file_base_path + f'tasks/problem{i}.png', file_base_path + f'tasks/problem{i}_{h}_{w}.png']
                result_path = file_base_path + f'results/result{i}_{h}_{w}_{j}.txt'

                if os.path.exists(result_path):
                    continue

                while True:
                    print('================================================================================')
                    print(f'Next task: {i} {h} {w} {j}')
                    Agent.print_agents(agents=agents)

                    cnt += 1
                    if cnt == 10:
                        cnt = 0

                        agent = Agent.find_free_agent(agents=agents)
                        if agent is not None:
                            print('find free agent!')

                            time.sleep(10)
                            thread = threading.Thread(target=run_task, args=(lock, agent, message, files, result_path))
                            thread.start()

                            break
                        
                        else:
                            print('No free agent :(')
                    
                    else:
                        print(f'Wait {cnt}')

                    time.sleep(3)


def experiment(task_generator='calculate_expression', method='step_by_step', num_agents=5, num_data=30):
    #print_all_module_versions()

    lock = threading.RLock()
    agents = set_agents(lock=lock)

    print('!')


    # generate task
    # - data/task_{}/tasks/...
    # - dtat/task_{}/solutions/...


    # regenerate task by the method
    # - data/task_{}/tasks_by_{method}/...
    # or
    # - data/task_{}/tasks/..._by_{method}
    # - data/taks_{}/solutions/..._by_{method}


    # do task
    # - data/taks_{}/results/...
    tasks = './data/task_1/'
    experiments_per_task = 3
    run_tasks(lock=lock, agents=agents, task_path=tasks, experiments_per_task=experiments_per_task)


    # check accuracy
    # - data/task_{}/result.csv


    return


if __name__ == "__main__":
    experiment()