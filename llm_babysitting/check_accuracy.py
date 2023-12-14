from gpt_crawler.crawler import GptCrawler
from gpt_crawler.agent import GptAgentState

import threading
import time
import os
import colorama
from colorama import Fore
import traceback
import re

colorama.init()

def extract_answer_in_line(line):
    res = list(re.findall(r'-?−?(?:\d+(?:[,]\d+)*)(?:[.]\d+)?', line))
    return res

def extract_answer(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    answers = []
    for i, line in enumerate(lines):
        if 'answer is' in line:
            answers.extend(extract_answer_in_line(line.split('answer is')[1]))
            if i+1 < len(lines): answers.extend(extract_answer_in_line(lines[i+1]))
                
        elif 'is approximately' in line:
            answers.extend(extract_answer_in_line(line.split('is approximately')[1]))
            if i+1 < len(lines): answers.extend(extract_answer_in_line(lines[i+1]))

        if len(answers) > 0:
            return answers

    if len(answers) > 0:
        return answers

    for i, line in enumerate(lines):
        if ' is' in line:
            answers.extend(extract_answer_in_line(line.split(' is')[1]))
            if i+1 < len(lines): answers.extend(extract_answer_in_line(lines[i+1]))
    
    return answers


def main():

    tabs = [
        'DC814929503E28937F532641A3A830A0'
    ]

    gpt_crawler = GptCrawler(tabs=tabs)

    gpt_crawler.print_window_handles()
    


    base_path = 'C:/Users/LeeYuseop/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/llm_babysitting/data/task_1/'

    result_path = base_path + 'result2.txt'
    results_path = base_path + 'results/'
    answers_path = base_path + 'answers/'

    for i in range(1, 31):
        True #

    file_list = os.listdir(results_path)

    for i, file_name in enumerate(file_list):
        #if i < 486: continue
        if 'url' in file_name: continue

        file_path = results_path + file_name

        result_info = file_name[6:-4]
        problem_number = result_info.split('_')[0]
        iteration_number = result_info.split('_')[-1]
        method = result_info[len(problem_number)+1:-len(iteration_number)-1]

        answers = extract_answer(results_path+file_name)

        if (file_name == 'result15_357_1.txt' or
            file_name == 'result15_357_2.txt' or
            file_name == 'result15_357_3.txt' or
            file_name == 'result15_CoT_noOCR_1.txt' or
            file_name == 'result22_7_7_2.txt'): answers = [0]
        if (file_name == 'result18_2.txt'): answers = [-5]
        if (file_name == 'result22_3.txt'): answers = ['nan']
        if (file_name == 'result23_357_3.txt' or
            file_name == 'result23_7_7_2.txt' or
            file_name == 'result23_357_2.txt'): answers = ['10^100']
        if (file_name == 'result23_CoT_noOCR_2.txt'): answers = ['1.036*10^11']

        print(f'#{i:3d}\t{problem_number}\t{method}\t{iteration_number}\t{answers}')

        if len(answers) == 1:
            print(Fore.BLUE, f'Answer: {answers[0]}', Fore.RESET)
            with open(result_path, 'a', encoding='utf-8') as file:
                file.write(f'{problem_number}\t{method}\t{iteration_number}\t{answers[0]}\n')
            continue
        
        '''else:
            print(Fore.YELLOW, 'Try to crawl again', Fore.RESET)
            url_file = results_path+file_name[:-4]+'_url.txt'
            with open(url_file, 'r', encoding='utf-8') as file:
                url = file.read()

            gpt_crawler.driver.get(url)

            time.sleep(3)

            conversations = gpt_crawler.get_conversations(tab_index=0)

            #print(conversations)

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(conversations[-1])

            time.sleep(1)


        # Try again

        answers = extract_answer(results_path+file_name)

        if len(answers) == 1:
            print(Fore.BLUE, f'Answer: {answers[0]}', Fore.RESET)
            with open(result_path, 'a', encoding='utf-8') as file:
                file.write(f'{problem_number}\t{method}\t{iteration_number}\t{answers[0]}\n')

        else:
            print(Fore.RED, f"I can't find answer :(\t{file_name}\n{url}", Fore.RESET)'''

        


    print(len(file_list))



if __name__ == "__main__":
    main()