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


def print_all_module_versions():
    print("Installed Packages:")
    print("===================")
    installed_packages = pkg_resources.working_set
    for package in installed_packages:
        print(f"{package.key} : {package.version}")
    print()


class CrawlerState(Enum):
    INITIALIZING = auto()
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()
    ERROR = auto()

class GptCrawlerState(CrawlerState):
    NEW_CHAT = auto()
    AWAITING_INPUT = auto()
    INPUTTING = auto()
    RESPONDING = auto()
    DELETING = auto()
    DELETED = auto()

    REGENERATE_ERROR = auto()
    LIMIT_ERROR = auto()


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
    '''
    def __init__(self, num_tabs=0, tabs=[], start=True, use_debugger=True, use_haedless=False, implicityly_wait=10):
        self.num_tabs = max(num_tabs, len(tabs))
        self.tabs = tabs
        while len(self.tabs) < self.num_tabs:
            self.tabs.append(None)
        self.state = [CrawlerState.INITIALIZING for _ in range(self.num_tabs)]
        self.error_messages = [None for _ in range(self.num_tabs)]
            
        self.lock = threading.RLock()
        self.current_lock_index = -1
        self.lock_counter = 0

        if start: self.start_chrome_driver(use_debugger=use_debugger, use_headless=use_haedless, implicityly_wait=implicityly_wait)
        else: self.driver = None


    def start_chrome_driver(self, use_debugger=True, use_headless=False, implicityly_wait=10):
        chrome_options = webdriver.ChromeOptions()

        if use_debugger:
            # Connect to a Chrome browser that is already running
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        if use_headless:
            chrome_options.add_argument("--headless")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(implicityly_wait)

        if not use_debugger:
            self.num_tabs = 1
            self.tabs.append(self.driver.current_window_handle)
            

    def open_tabs(self):
        for _ in range(self.num_tabs - 1):
            self.driver.execute_script("window.open('about:blank', '_blank');")
            self.tabs.append(self.driver.window_handles[-1])


    def switch_tab(self, tab_index):
        self.lock_acquire(tab_index)

        try:
            if 0 <= tab_index < len(self.tabs):
                self.driver.switch_to.window(self.tabs[tab_index])
            else:
                raise ValueError("No tab assigned. Please select a valid tab index.")
            
        finally:
            self.lock_release()

    
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


    def lock_acquire(self, index):
        self.lock.acquire()
        self.current_lock_index = index
        self.lock_counter += 1
        
        self.switch_tab(tab_index=index)


    def lock_release(self):
        self.lock_counter -= 1
        if self.lock_count == 0:
            self.current_lock_index = -1
        self.lock.release()


    def wait(self, wait_time=1):
        lock_index = self.current_lock_index
        lock_counter = self.lock_counter

        self.current_lock_index = -1
        self.lock_counter = 0

        for _ in range(lock_counter): self.lock.release()

        time.sleep(wait_time)

        while lock_counter > 0:
            self.lock.acquire()
            lock_counter -= 1
        self.current_lock_index = lock_index
        
        self.switch_tab(tab_index=lock_index)

    
    def get_state(self, tab_index):
        if 0 <= tab_index < len(self.tabs):
            self.driver.switch_to.window(self.tabs[tab_index])
        else:
            raise ValueError("No tab assigned. Please select a valid tab index.")



class GptCrawler(Crawler):

    def start_new_chat(self, tab_index=-1, model='gpt-3.5', message='', files=[], max_attempts=99999):
        if tab_index < 0 or tab_index >= len(self.tabs):
            raise ValueError("No tab assigned. Please select a valid tab index.")
        if not message and not files:
            raise ValueError("Please provide either a message or an file(s).")
        
        self.lock_acquire(index=tab_index)
        
        try:
            # Generate the URL according to the model version.
            gpt_url = 'https://chat.openai.com/'
            if model == 'gpt-3.5': gpt_url += '?model=text-davinci-002-render-sha'
            elif model == 'gpt-4': gpt_url += '?model=gpt-4'
            else: raise ValueError("The model provided is invalid. Please check the model.")
            self.driver.get(gpt_url)

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
                raise NoSuchElementException(f"Tried {max_attempts} times but couldn't find the 'How can I help you today' and 'Message ChatGPT...' strings.")
            self.state[tab_index] = GptCrawlerState.NEW_CHAT

            self.send_message(tab_index=tab_index, message=message, files=files, max_attempts=max_attempts)

        except Exception as e:
            self.state[tab_index] = GptCrawlerState.ERROR
            self.error_messages[tab_index] = e
            raise e
        
        finally:
            self.lock.release()

    
    def send_message(self, tab_index=-1, message='', files=[], max_attempts=99999):
        if tab_index < 0 or tab_index >= len(self.tabs):
            raise ValueError("No tab assigned. Please select a valid tab index.")
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
            self.state[tab_index] = GptCrawlerState.ERROR
            self.error_messages[tab_index] = e
            raise e

        finally:
            self.lock_release()


    def input_files(self, tab_index=-1, files=[], max_attempts=99999):
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


            # If message contains '\n' characters, change '\n' to Shift+Enter.
            for line in message.split('\n'):
                text_area.send_keys(line)
                text_area.send_keys(Keys.SHIFT + Keys.ENTER)
            text_area.send_keys(Keys.BACKSPACE)

        finally:
            self.lock_release()

    
    def click_send_button(self, tab_index=-1, max_attempts=99999):
        self.lock_acquire(index=tab_index)

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
                    regenerate_button.click()
                    self.state[tab_index] = GptCrawlerState.REGENERATE_ERROR
                
                # limit error
                limit_error_box = self.driver.find_elements(By.CSS_SELECTOR, 'div[class="flex items-center gap-6"]')
                if len(limit_error_box) == 1:
                    self.error_messages[tab_index] = limit_error_box[0].text
                    self.state[tab_index] = GptCrawlerState.LIMIT_ERROR
                    #stop_program(agent, error_text)
                    #미완성
                
                self.state[tab_index] = GptCrawlerState.ERROR

            else:
                send_button = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-testid="send-button"]')
                if len(send_button) == 1:
                    if self.state[tab_index] != GptCrawlerState.INPUTTING:
                        self.state[tab_index] = GptCrawlerState.AWAITING_INPUT
                else:
                    self.state[tab_index] = GptCrawlerState.RESPONDING

        except Exception as e:
            self.state[tab_index] = GptCrawlerState.ERROR
            self.error_messages[tab_index] = e
            raise e

        finally:
            self.lock_release()



def test():
    print_all_module_versions()

    crawler = Crawler()


if __name__ == "__main__":
    test()




'''
def stop_program(agent, error_text):
    print(time.strftime('[%H:%M:%S]'), f"agent #{agent['id']} releases lock")
    agent['lock'].release()

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
        time.sleep(time_diff+60)  # 추출한 시간까지 대기
        print("대기 완료!")

    else:
        print("시간 정보를 찾을 수 없습니다.")

    agent['lock'].acquire()
    print(time.strftime('[%H:%M:%S]'), f"agent #{agent['id']} acquires lock")
    time.sleep(1)





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