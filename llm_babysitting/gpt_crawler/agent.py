# Last updated: 2023. 12. 03.

import pkg_resources
from enum import Enum
import colorama
from colorama import Fore
import textwrap
import gpt_crawler.crawler as crawler


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
        if gpt_crawler is None: self.gpt_crawler = crawler.GptCrawler()
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

        colorama.init()


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
            self.print_lines("lines should be either a string or a list of strings.", width=width, front=front)


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
            except Exception as e:
                self.error_message = e
    
    
    def update_state(self):
        try:
            if self.gpt_crawler is None:
                print("GptCrawler does not exist.")
                return
            
            if self.tab_index == -1:
                return
            
            if self.state == GptAgentState.PREPARATION:
                url = None
            if self.url is None:
                if self.state == GptAgentState.AWAITING_INPUT or self.state == GptAgentState.RESPONDING or self.state == GptAgentState.FINISHED:
                    self.url = self.gpt_crawler.get_url(self.tab_index)

            self.check_model(model=self.model)

            self.conversations = self.gpt_crawler.get_conversations(self.tab_index)

            if self.state == GptAgentState.RESPONDING:
                crawler_state = self.gpt_crawler.get_state(self.tab_index)
                #self.gpt_crawler.
                True

            if self.state != GptAgentState.ERROR:
                self.error_message = None
        
        except Exception as e:
            self.state = GptAgentState.ERROR
            self.error_message = e


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

        except Exception as e:
            self.error_message = e



    



def main():
    gpt_crawler = crawler.GptCrawler()

    agent = GptAgent(gpt_crawler=gpt_crawler)


if __name__ == "__main__":
    main()