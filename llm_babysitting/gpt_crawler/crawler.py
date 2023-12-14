# Last updated: 2023. 12. 03.

# C:\Program Files\Google\Chrome\Application> chrome.exe --remote-debugging-port=9222

import pkg_resources
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import threading
import time
from enum import Enum, auto
import colorama
from colorama import Fore
import traceback
import re


def print_all_module_versions():
    print("Installed Packages:")
    print("===================")
    installed_packages = pkg_resources.working_set
    for package in installed_packages:
        print(f"{package.key} : {package.version}")
    print()


def make_error_message(trace, error):
    filename = trace.filename.split('LLM_Babysitting_Project\\')[-1]
    return f"File: {filename}, Method: {trace.name}, Line: {trace.lineno}\n{error}"


class CrawlerState(Enum):
    INITIALIZING = auto()
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()
    ERROR = auto()

class GptCrawlerState(Enum):
    INITIALIZING = auto()
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()
    ERROR = auto()

    NEW_CHAT = auto()
    AWAITING_INPUT = auto()
    INPUTTING = auto()
    RESPONDING = auto()
    DELETING = auto()
    DELETED = auto()

    REGENERATE_ERROR = auto()
    LIMIT_ERROR = auto()
    ERROR_HANDLED = auto()


class Crawler:
    '''
    driver: webdriver or None
    num_tabs: int
    tabs: str list
    states: list of CrawlerState
    error_messages: list of (str or None)
    start: bool
    use_debugger: bool
    use_headless: bool
    implicityly_wait: int
    lock: threading.RLock
    current_lock_index: int
    lock_counter: int
    debug_mode: bool
    '''
    def __init__(self, num_tabs=0, tabs=[], lock=None, start=True, use_debugger=True, use_haedless=False, implicityly_wait=10, debug_mode=False):
        self.num_tabs = max(num_tabs, len(tabs))
        self.tabs = tabs
        while len(self.tabs) < self.num_tabs:
            self.tabs.append(None)
        self.state = [CrawlerState.INITIALIZING for _ in range(self.num_tabs)]
        self.error_messages = [None for _ in range(self.num_tabs)]

        if lock is None: self.lock = threading.RLock()
        else: self.lock = lock
        self.current_lock_index = -1
        self.lock_counter = 0

        self.debug_mode = debug_mode

        if start: self.start_chrome_driver(use_debugger=use_debugger, use_headless=use_haedless, implicityly_wait=implicityly_wait)
        else: self.driver = None


    def start_chrome_driver(self, use_debugger=True, use_headless=False, implicityly_wait=10):
        self.print_debug_message(f"function: start_chrome_driver")

        chrome_options = webdriver.ChromeOptions()

        if use_debugger:
            # Connect to a Chrome browser that is already running
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        if use_headless:
            chrome_options.add_argument("--headless")

        self.print_debug_message(f"- Finish to set options")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(implicityly_wait)

        self.print_debug_message(f"- Success for connecting to chrome driver")

        if not use_debugger:
            self.num_tabs = 1
            self.tabs.append(self.driver.current_window_handle)
            

    def open_tabs(self):
        for _ in range(self.num_tabs - 1):
            self.driver.execute_script("window.open('about:blank', '_blank');")
            self.tabs.append(self.driver.window_handles[-1])


    def switch_tab(self, tab_index):
        if 0 <= tab_index < len(self.tabs):
            self.driver.switch_to.window(self.tabs[tab_index])
            if self.driver.current_window_handle != self.tabs[tab_index]:
                time.sleep(3)
            self.print_debug_message('function: switch_tab (Success)')
        else:
            self.print_debug_message('function: switch_tab (Fail)')
            raise ValueError(f"No tab assigned. Please select a valid tab index: {tab_index}")

    
    def get_url(self, tab_index):
        self.lock_acquire(tab_index)

        try:
            url = self.driver.current_url
        finally:
            self.lock_release()
        
        return url


    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.tabs = []


    def print_window_handles(self):
        self.lock.acquire()

        try:
            # get a current window handle and all of window handles
            window_handles = self.driver.window_handles
            current_window_handle = self.driver.current_window_handle

            print("current window handle:", current_window_handle)
            print("current_window_url:", self.driver.current_url)

            # print all of window handles and each url
            print("window_handles:")
            for window_handle in window_handles:
                # switch the window to get the url of the corresponding window
                self.driver.switch_to.window(window_handle)
                # current_url = None if the window is not connected to any url
                try:
                    current_url = self.driver.current_url
                except Exception:
                    current_url = None

                print("-", window_handle, current_url)
            print()

            # Return to the original window
            self.driver.switch_to.window(current_window_handle)
        
        finally:
            self.lock.release()

    
    def print_debug_message(self, debug_message=''):
        if not self.debug_mode: return
        base = f'{Fore.BLUE}#{self.current_lock_index:2d}-{self.lock_counter}({threading.current_thread().name}) {Fore.RESET}'
        debug_message = base + debug_message.replace('\n','\n'+base)
        print(debug_message)


    def lock_acquire(self, index):
        self.lock.acquire()

        self.current_lock_index = index
        self.lock_counter += 1

        self.print_debug_message(f'{Fore.YELLOW}function: lock_acquire #{index}{Fore.RESET}')
        self.switch_tab(tab_index=index)


    def lock_release(self):
        self.lock_counter -= 1

        self.print_debug_message(f'{Fore.GREEN}function: lock_relese #{self.current_lock_index}{Fore.RESET}')

        if self.lock_counter == 0:
            self.current_lock_index = -1
        self.lock.release()


    def wait(self, wait_time=1):
        self.print_debug_message('function: wait')
        lock_index = self.current_lock_index
        lock_counter = self.lock_counter
        self.print_debug_message(f'- lock index: {lock_index}')
        self.print_debug_message(f'- lock counter: {lock_counter}')

        self.current_lock_index = -1
        self.lock_counter = 0

        for _ in range(lock_counter):
            self.lock.release()

        time.sleep(wait_time)

        for _ in range(lock_counter):
            self.lock.acquire()

        self.current_lock_index = lock_index
        self.lock_counter = lock_counter
        
        self.switch_tab(tab_index=lock_index)

        self.print_debug_message("Finish to wait")

    
    def get_state(self, tab_index):
        if 0 <= tab_index < len(self.tabs):
            return self.state[tab_index]
        else:
            raise ValueError(f"No tab assigned. Please select a valid tab index: {tab_index}")



class GptCrawler(Crawler):

    def start_new_chat(self, tab_index=-1, model='gpt-3.5', message='', files=[], max_attempts=99999):
        if tab_index < 0 or tab_index >= len(self.tabs):
            current_trace = traceback.extract_stack()[-1]
            raise ValueError(make_error_message(current_trace, f"No tab assigned. Please select a valid tab index: {tab_index}"))
        if not message and not files:
            current_trace = traceback.extract_stack()[-1]
            raise ValueError(make_error_message(current_trace, "Please provide either a message or an file(s)."))
        
        self.print_debug_message(f'function: start_new_chat')

        self.lock_acquire(index=tab_index)
        
        try:
            # Generate the URL according to the model version.
            gpt_url = 'https://chat.openai.com/'
            if model == 'gpt-3.5': gpt_url += '?model=text-davinci-002-render-sha'
            elif model == 'gpt-4': gpt_url += '?model=gpt-4'
            else: raise ValueError("The model provided is invalid. Please check the model.")
            self.driver.get(gpt_url)
            self.print_debug_message(f'{gpt_url}')

            # Find 'How can I help you today?' and 'Message ChatGPT…' strings
            attempts = 0
            while attempts < max_attempts:
                html_content = self.driver.page_source
                if 'How can I help you today?' in html_content and 'Message ChatGPT…' in html_content:
                    break
                else:
                    attempts += 1
                    self.wait(wait_time=1)
            if attempts == max_attempts:
                current_trace = traceback.extract_stack()[-1]
                raise NoSuchElementException(make_error_message(current_trace, f"Tried {max_attempts} times but couldn't find the 'How can I help you today' and 'Message ChatGPT...' strings."))
            
            self.state[tab_index] = GptCrawlerState.NEW_CHAT
            self.print_debug_message(f'success for connect to chatGPT')

            self.send_message(tab_index=tab_index, message=message, files=files, max_attempts=max_attempts)

        except Exception as e:
            current_trace = traceback.extract_stack()[-1]
            error_message = make_error_message(current_trace, str(e))

            self.state[tab_index] = GptCrawlerState.ERROR
            self.error_messages[tab_index] = error_message
            raise error_message
        
        finally:
            self.lock_release()

    
    def send_message(self, tab_index=-1, message='', files=[], max_attempts=99999):
        if tab_index < 0 or tab_index >= len(self.tabs):
            raise ValueError(f"No tab assigned. Please select a valid tab index: {tab_index}")
        if not message and not files:
            raise ValueError("Please provide either a message or an image(s).")
        
        self.lock_acquire(index=tab_index)

        try:
            self.state[tab_index] = GptCrawlerState.INPUTTING
            self.input_files(tab_index=tab_index, files=files, max_attempts=max_attempts)
            self.input_message(tab_index=tab_index, message=message, max_attempts=max_attempts)
            self.wait(wait_time=1)
            self.click_send_button(tab_index=tab_index, max_attempts=max_attempts)
            self.state[tab_index] = GptCrawlerState.RESPONDING

        except Exception as e:
            current_trace = traceback.extract_stack()[-1]
            error_message = make_error_message(trace=current_trace, error="Please provide either a message or an file(s).")
            
            self.error_messages[tab_index] = error_message
            self.state[tab_index] = GptCrawlerState.ERROR
            raise ValueError(e)

        finally:
            self.lock_release()


    def input_files(self, tab_index=-1, files=[], max_attempts=99999):
        if not files: return

        self.lock_acquire(index=tab_index)

        try:
            # Find file input element
            attempts = 0
            while attempts < max_attempts:
                try:
                    file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type=file]")
                    break
                except:
                    attempts += 1
                    self.wait(wait_time=1)
            if attempts == max_attempts:
                raise NoSuchElementException(f"Tried {max_attempts} times but couldn't find the 'input[type=file]' element.")

            for file in files:
                # I don't know why it is duplicate, so before to upload files, delete all of the files.
                delete_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[class="absolute right-1 top-1 -translate-y-1/2 translate-x-1/2 rounded-full border border-white bg-gray-500 p-0.5 text-white transition-colors hover:bg-black hover:opacity-100 group-hover:opacity-100 md:opacity-0"]')
                for delete_button in delete_buttons:
                    delete_button.click()
                    time.sleep(1)

                file_input.send_keys(file)
                time.sleep(1)
        
        finally:
            self.lock_release()


    def input_message(self, tab_index=-1, message='', max_attempts=99999):
        self.lock_acquire(index=tab_index)
        self.print_debug_message(f'function: input_message')

        try:
            # find a text input area, and input a message
            attempts = 0
            while attempts < max_attempts:
                try:
                    text_area = self.driver.find_element(By.ID, 'prompt-textarea')
                    break
                except:
                    attempts += 1
                    self.wait(wait_time=1)
            if attempts == max_attempts:
                raise NoSuchElementException(f"Tried {max_attempts} times but couldn't find the 'prompt-textarea' element.")
            self.print_debug_message(f'- Find a text area!')


            # If message contains '\n' characters, change '\n' to Shift+Enter.
            for line in message.split('\n'):
                text_area.send_keys(line)
                text_area.send_keys(Keys.SHIFT + Keys.ENTER)
            text_area.send_keys(Keys.BACKSPACE)

            self.print_debug_message(f'- Success to input the message!')

        finally:
            self.lock_release()

    
    def click_send_button(self, tab_index=-1, max_attempts=99999):
        self.lock_acquire(index=tab_index)
        self.print_debug_message('function: click_send_button')

        try:
            # find a text input area, and input a message
            attempts = 0
            while attempts < max_attempts:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-testid="send-button"]')
                    if send_button.is_enabled:
                        break
                finally:
                    attempts += 1
                    self.wait(wait_time=1)
            if attempts == max_attempts:
                raise NoSuchElementException(f"Tried {max_attempts} times but couldn't find the 'button[data-testid=\"send-button\"]' element or send button is not enabled.")

            send_button.click()

        finally:
            self.lock_release()

    
    def update_state(self, tab_index):
        self.lock_acquire(index=tab_index)

        try:
            # If there exists any error, then there is no message box.
            message_box = self.driver.find_elements(By.CSS_SELECTOR, 'div[class="relative flex h-full flex-1 items-stretch md:flex-col"]')
            if len(message_box) == 0:
                # regenerate error
                regenerate_button = self.driver.find_elements(By.CSS_SELECTOR, 'button[class="btn relative btn-primary m-auto"]')
                if len(regenerate_button) == 1:
                    current_trace = traceback.extract_stack()[-1]
                    error_message = make_error_message(trace=current_trace, error='Regenerate error e.g. "Hmm...something seems to have gone wrong."')
                    
                    self.error_messages[tab_index] = error_message
                    self.state[tab_index] = GptCrawlerState.REGENERATE_ERROR

                    regenerate_button[0].click()
                    self.wait(1)

                    return
                
                # limit error
                limit_error_box = self.driver.find_elements(By.CSS_SELECTOR, 'div[class="flex items-center gap-6"]')
                if len(limit_error_box) == 1:
                    limit_error_text = limit_error_box[0].text

                    current_trace = traceback.extract_stack()[-1]
                    error_message = make_error_message(trace=current_trace, error=limit_error_text)
                    
                    self.error_messages[tab_index] = error_message
                    self.state[tab_index] = GptCrawlerState.LIMIT_ERROR
                    
                    self.wait_limit_error(limit_error_text)
                    
                    self.state[tab_index] = GptCrawlerState.ERROR_HANDLED

                    return
                
                current_trace = traceback.extract_stack()[-1]
                error_message = make_error_message(trace=current_trace, error="I don't know what is wrong :(")
                
                self.error_messages[tab_index] = error_message
                self.state[tab_index] = GptCrawlerState.ERROR

            else:
                send_button = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-testid="send-button"]')
                if len(send_button) == 1:
                    if self.state[tab_index] != GptCrawlerState.INPUTTING:
                        self.error_messages[tab_index] = None
                        self.state[tab_index] = GptCrawlerState.AWAITING_INPUT
                else:
                    self.error_messages[tab_index] = None
                    self.state[tab_index] = GptCrawlerState.RESPONDING

        except Exception as e:
            current_trace = traceback.extract_stack()[-1]
            error_message = make_error_message(trace=current_trace, error=str(e))
            
            self.error_messages[tab_index] = error_message
            self.state[tab_index] = GptCrawlerState.ERROR

            raise ValueError(error_message)

        finally:
            self.lock_release()

    
    def get_conversations(self, tab_index):
        self.lock_acquire(tab_index)

        try:
            # Get conversation elements
            conversation_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid^="conversation-turn-"]')

            # if there is any conversation, then return "Not Started"
            if len(conversation_elements) == 0: return []

            # Extracting text from elements.
            conversations = []
            for conversation_element in conversation_elements:
                try:
                    conversation = conversation_element.text
                except:
                    conversation = 'Error :('
                
                conversations.append(conversation)

            time.sleep(1)
            
            return conversations

        except Exception as e:
            current_trace = traceback.extract_stack()[-1]
            error_message = make_error_message(trace=current_trace, error=str(e))
            
            self.error_messages[tab_index] = error_message
            self.state[tab_index] = GptCrawlerState.ERROR

            raise ValueError(error_message)

        finally:
            self.lock_release()

            
    def delete_chat(self, tab_index, target_url=None, max_attempts=99999):
        self.lock_acquire(tab_index)

        try:
            self.print_debug_message('function: delete_chat')
            if target_url is None:
                target_url = self.get_url(tab_index)
            
            # Go to the chatGPT page
            url = "https://chat.openai.com/"
            self.driver.get(url)

            # Wait until the left bar appears.
            attempts = 0
            while attempts < max_attempts:
                try:
                    bar_element = self.driver.find_element(By.CSS_SELECTOR, 'div[class="group relative active:opacity-90"]')
                    break
                except:
                    attempts += 1
                    self.wait(wait_time=1)
            if attempts == max_attempts:
                current_trace = traceback.extract_stack()[-1]
                raise NoSuchElementException(make_error_message(current_trace, f"Tried {max_attempts} times but couldn't find the left bar"))

            # Get chat elements
            cnt=0
            chat_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[class="group relative active:opacity-90"]')
            for chat_element in chat_elements:
                cnt += 1
                if cnt > 10: break
                chat_url = chat_element.find_element(By.XPATH, './*').get_attribute('href')

                if target_url is None or chat_url == target_url:
                    # Sometimes it doesn't work. so try 10 times.
                    for i in range(10):
                        try:
                            chat_element.click()
                            time.sleep(1)

                            button = chat_element.find_element(By.TAG_NAME, 'button')
                            button.click()
                            time.sleep(1)

                            menuitems = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="menuitem"]')
                            menuitems[2].click()
                            time.sleep(1)

                            delete_button = self.driver.find_element(By.CSS_SELECTOR, 'button[class="btn relative btn-danger"]')
                            delete_button.click()
                            time.sleep(1)

                            break
                        except:
                            self.wait(1)

        finally:
            self.lock_release()



    def wait_limit_error(self, error_text):
        # 시간 정보 추출을 위한 정규 표현식 패턴
        time_pattern = r'after (\d+:\d+ [AP]M)'

        # 정규 표현식을 사용하여 시간 정보 추출
        match = re.search(time_pattern, error_text)

        if match:
            extracted_time = match.group(1)
            print("추출된 시간 정보:", extracted_time)

            # 시간 문자열을 파싱하여 시간 정보 추출
            time_format = "%I:%M %p"  # 시간 형식 지정

            # 현재 날짜와 시간으로 설정
            current_time = time.localtime()
            target_time = time.strptime(extracted_time + " " + time.strftime("%Y-%m-%d"), time_format + " %Y-%m-%d")

            # 시간 비교를 위한 시간 차 계산
            time_diff = time.mktime(target_time) - time.mktime(current_time)

            if time_diff < 0:
                time_diff += 86400

            print(f"{time_diff}초 동안 대기합니다.")

            self.wait(time_diff+60)  # 추출한 시간까지 대기

            print("대기 완료!")

        else:
            print("시간 정보를 찾을 수 없습니다.")




def test_crawler():
    print_all_module_versions()

    tabs = [
        'F634AA33A771E0B357AB34456D632A51',
        '503CF570207676C37CA2147F76A5C955',
        '3C48605445BF58A6DB186249AAFC21FC',
        '799D9EFB9D69C473688CD64135C93D42',
        '69539F4F2B3D522C56564BA0744F3D49'
    ]

    crawler = Crawler(tabs=tabs)
    crawler.print_window_handles()


if __name__ == "__main__":
    test_crawler()




'''






# check a gpt's status
def check_status(driver=None, agent=None, window_handle=None, url=None):
    if driver is None: driver = DEFAULT_DRIVER

    check_window_url(driver=driver, agent=agent, window_handle=window_handle, url=url)

    # Use a existence of the "Send message" button
    try:
        # If there exists any error, then there is no message box.
        message_box = driver.find_elements(By.CSS_SELECTOR, 'div[class="relative flex h-full flex-1 items-stretch md:flex-col"]')
        if len(message_box) == 0:
            # regenerate error
            regenerate_button = driver.find_elements(By.CSS_SELECTOR, 'button[class="btn relative btn-primary m-auto"]')
            if len(regenerate_button) == 1:
                regenerate_button.click()
                return AgentStatus.ERROR
            
            # limit error
            limit_error_box = driver.find_elements(By.CSS_SELECTOR, 'div[class="flex items-center gap-6"]')
            if len(limit_error_box) == 1:
                error_text = limit_error_box[0].text
                stop_program(agent, error_text)
                return AgentStatus.ERROR
            
            return AgentStatus.ERROR

        else:
            send_button = driver.find_elements(By.CSS_SELECTOR, 'button[data-testid="send-button"]')
            if len(send_button) == 1:
                return AgentStatus.WAITING
            else:
                return AgentStatus.RESPONDING

    except:
        return AgentStatus.ERROR

'''