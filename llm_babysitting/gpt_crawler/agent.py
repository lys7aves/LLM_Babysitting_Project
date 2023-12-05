# Last updated: 2023. 12. 03.

from crawler import GptCrawler, GptCrawlerState

import pkg_resources
from enum import Enum
import colorama
from colorama import Fore
import textwrap
import time
import threading
import traceback


colorama.init()

def print_all_module_versions():
    print("Installed Packages:")
    print("===================")
    installed_packages = pkg_resources.working_set
    for package in installed_packages:
        print(f"{package.key} : {package.version}")
    print()


class GptAgentState(Enum):
    PREPARATION = 1
    START = 2
    AWAITING_INPUT = 3
    INPUTTING = 4
    RESPONDING = 5
    FINISHED = 6
    ERROR = 7


class GptAgent:
    '''
    gpt_crawler: clawler.GptCrawler or None
    tab_index: int
    url: str or None
    model: str
    name: str
    conversations: str list
    state: GptAgentState
    error_message: str or None
    max_attempts: int
    '''
    def __init__(self, gpt_crawler=None, tab_index=-1, url=None, model='gpt-3.5', name='chatGPT', conversations=[], state=GptAgentState.PREPARATION):
        if gpt_crawler is None: self.gpt_crawler = GptCrawler()
        else: self.gpt_crawler = gpt_crawler

        self.tab_index = tab_index
        self.url = url

        self.check_model(model=model)
        self.model = model

        self.name = name
        self.conversations = conversations
        self.state = state

        self.error_message = None
        self.max_attempts = 99999


    def __str__(self):
        return f"Agent #{self.name}"
    

    def print_info(self, width=80):
        if self.tab_index == self.gpt_crawler.current_lock_index:
            print(Fore.YELLOW, end='')

        print(f"Agent Information ({self.name}):")
        print("==================")
        print(f"Tab index: {self.tab_index}")
        print(f"URL: {self.url}")
        print(f"Model: {self.model}")
        print(f"Conversations:")
        self.print_lines(lines=self.conversations, width=width)
        print(f"State: {self.state}")
        if self.state == GptAgentState.ERROR:
            print(f"Error message:")
            self.print_lines(self.error_message, width=width)
        print()

        print(Fore.RESET, end='')


    def print_lines(self, lines, width=80, front='| '):
        if lines is None:
            print(front + 'None')

        elif isinstance(lines, str):
            wrapped_lines = textwrap.fill(lines, width=width-len(front))
            formatted_lines = front + wrapped_lines.replace('\n', '\n'+front)
            print(formatted_lines)

        elif isinstance(lines, list):
            for i, line in enumerate(lines):
                if i > 0: print(front[:-3])
                self.print_lines(line, width=width, front=front+'| ')

        else:
            self.print_lines(f"lines should be either a string or a list of strings.\nlines: {lines}", width=width, front=front)


    def is_valid_model(self, model):
        if model == 'gpt-3.5': return True
        if model == 'gpt-4': return True

        return False
    

    def check_model(self, model):
        if not self.is_valid_model(model=model):
            raise ValueError("The model provided is invalid. Please check the model.")

    
    def start(self, message='', files=[]):
        '''if not message and not files:
            print("Please provide either a message or an file(s).")
            return'''
        
        if self.state != GptAgentState.PREPARATION:
            print(f"{self.__str__} is not yet prepared.")
            return

        self.state = GptAgentState.START

        if not message and not files:
            self.state = GptAgentState.AWAITING_INPUT
        else:
            try:
                self.state = GptAgentState.INPUTTING
                self.gpt_crawler.start_new_chat(tab_index=self.tab_index, model=self.model, message=message, files=files, max_attempts=self.max_attempts)
                self.state = GptAgentState.RESPONDING
                # 스레드 만들어서 응답 기다리기
                thread = threading.Thread(target=self.wait_for_respond, args=())
                thread.start()
            except Exception as e:
                self.state = GptAgentState.ERROR
                self.error_message = "In the gpt_crawler.agent.start: " + str(e)
    
    
    def update_state(self):
        try:
            if self.gpt_crawler is None:
                print("GptCrawler does not exist.")
                return
            
            if self.tab_index == -1:
                print("No assigned tab found.")
                return
            
            self.gpt_crawler.update_state(self.tab_index)
            crawler_state = self.gpt_crawler.get_state(self.tab_index)
            if crawler_state == GptCrawlerState.NEW_CHAT: self.state = GptAgentState.START
            elif crawler_state == GptCrawlerState.AWAITING_INPUT: self.state = GptAgentState.AWAITING_INPUT
            elif crawler_state == GptCrawlerState.INPUTTING: self.state = GptAgentState.INPUTTING
            elif crawler_state == GptCrawlerState.RESPONDING: self.state = GptAgentState.RESPONDING
            elif crawler_state == GptCrawlerState.DELETING: self.state = GptAgentState.FINISHED
            elif crawler_state == GptCrawlerState.DELETED: self.state = GptAgentState.PREPARATION
            elif (crawler_state == GptCrawlerState.ERROR
                  or crawler_state == GptCrawlerState.REGENERATE_ERROR
                  or crawler_state == GptCrawlerState.LIMIT_ERROR):
                self.error_message = self.gpt_crawler.error_messages[self.tab_index]
                self.state = GptAgentState.ERROR
            else:
                self.error_message = f"Undefined crawler state: {crawler_state.name}"
                self.state = GptAgentState.ERROR


            if self.state == GptAgentState.PREPARATION:
                url = None
            if self.url is None:
                if self.state == GptAgentState.AWAITING_INPUT or self.state == GptAgentState.RESPONDING or self.state == GptAgentState.FINISHED:
                    self.url = self.gpt_crawler.get_url(self.tab_index)

            self.check_model(model=self.model)

            self.conversations = self.gpt_crawler.get_conversations(self.tab_index)

            if self.state != GptAgentState.ERROR:
                self.error_message = None
        
        except Exception as e:
            self.state = GptAgentState.ERROR
            self.error_message = "In the gpt_crawler.agent.update_state function: " + str(e)


    def send_message(self, message='', files=[]):
        if not message and not files:
            print("Please provide either a message or an file(s).")
            return
        
        if self.state != GptAgentState.AWAITING_INPUT:
            print(f"{self.__str__} is not yet prepared.")
            return

        try:
            self.state = GptAgentState.INPUTTING
            self.gpt_crawler.send_message(tab_index=self.tab_index, message=message, files=files, max_attempts=self.max_attempts)
            self.state = GptAgentState.RESPONDING
            # 스레드 만들어서 응답 기다리기
            thread = threading.Thread(target=self.wait_for_respond, args=())
            thread.start()

        except Exception as e:
            self.state = GptAgentState.ERROR
            self.error_message = "In the gpt_crawler.agent.send_message function: " + str(e)


    def wait_for_respond(self, max_attempts=99999):
        attempts = 0
        while attempts < max_attempts:
            self.update_state()
            self.conversations = self.gpt_crawler.get_conversations(tab_index=self.tab_index)

            if self.state != GptAgentState.RESPONDING:
                break

            attempts += 1
            time.sleep(1)

        if attempts == max_attempts:
            raise ValueError(f"Tried {max_attempts} times but couldn't receive a response.")
        

    def get_message(self):
        if len(self.conversations)%2 == 0:
            return self.conversations[-1]
        else:
            return ''

    
def print_agents(agents=[]):
    for agent in agents:
        agent.print_info()


def find_free_agent(agents=[]):
    for agent in agents:
        if agent.state == GptAgentState.PREPARATION:
            return agent
    
    return None


def do_task(agent, message='', files=[]):
    print('message:', message)
    print('files:', files)
    agent.start(message=message, files=files)

    while agent.state == GptAgentState.RESPONDING:
        time.sleep(1)
    

    if agent.state == GptAgentState.AWAITING_INPUT:
        print(agent.conversations[-1])
    else:
        print(Fore.RED, end='')
        print('Error on do_task :(')
        print(str(agent))
        print(agent.state.name)
        print(agent.error_message)
        traceback.print_exc()
        print(Fore.RESET)



def main():
    gpt_crawler = GptCrawler()

    agent = GptAgent(gpt_crawler=gpt_crawler)


if __name__ == "__main__":
    main()