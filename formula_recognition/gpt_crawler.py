# Last updated: 2023. 11. 28. 15:31

# C:\Program Files\Google\Chrome\Application> chrome.exe --remote-debugging-port=9222

#import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from enum import Enum
import os
import signal
import re
import threading

class AgentStatus(Enum):
    FREE = 'Free'
    NOT_STARTED = 'Not Started'
    WAITING = 'Waiting'
    RESPONDING = 'Responding'
    ERROR = 'Error'

DEFAULT_DRIVER = None
LOCK = threading.Lock()

# Connect to a chrome browser
def connect_browser():
    # Connect to a Chrome browser that is already running
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    global DEFAULT_DRIVER
    DEFAULT_DRIVER = driver

    return driver


def disconnect_browser(driver=None):
    if driver is None: driver = DEFAULT_DRIVER

    driver.quit()


def set_agent(agent=None, model=None, name=None, url=None, id=None, window_handle=None, conversations=[], status=AgentStatus.FREE, lock=LOCK):
    if agent is None:
        agent = {}
    
    if model is not None: agent['model'] = model
    if name is not None: agent['name'] = name
    agent['url'] = url
    agent['id'] = id
    if window_handle is not None: agent['window_handle'] = window_handle
    agent['conversations'] = conversations
    agent['status'] = status
    agent['lock'] = lock
    
    return agent


def start_new_chat(driver=None, agent=None, agent_name='ChatGPT', first_msg='', first_image=None, first_images=None, window_handle=None, model=None, lock=LOCK):
    if driver is None: driver = DEFAULT_DRIVER

    # if you know window handle, then switch to the window
    # else get a current window handle
    if window_handle is not None:
        # if you only know the number of window, then find the window handle
        if isinstance(window_handle, int): window_handle = driver.window_handles[window_handle]
        driver.switch_to.window(window_handle)
    else:
        window_handle = driver.current_window_handle

    agent = set_agent(agent=agent, name=agent_name, window_handle=window_handle, model=model, status=AgentStatus.NOT_STARTED, lock=lock)

    # Generate the URL according to the model version.
    gpt_url = 'https://chat.openai.com/'
    if model == 'gpt-3.5': gpt_url += '?model=text-davinci-002-render-sha'
    if model == 'gpt-4': gpt_url += '?model=gpt-4'
    driver.get(gpt_url)

    # Wait until the left bar appears.
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-projection-id]"))
    )


    # Send the first message

    ## If the model is gpt-4, then send image(s)
    if model == 'gpt-4':
        send_image(driver=driver, image_path=first_image, image_paths=first_images)

    ## Send the first_msg
    send_message(driver=driver, window_handle=window_handle, msg=first_msg)
    time.sleep(1)

    ## Get the respond
    get_message(driver=driver, agent=agent, turn=1)


    check_window_url(driver=driver, window_handle=window_handle)
    # Get a current url. This is a chatGPT's unique url.
    agent['url'] = driver.current_url
    # We can get a unique id from the url. For example in https://chat.openai.com/c/364f93f1-c1db-471a-ab66-5d2447a9ebf2, we can get /c/364f93f1-c1db-471a-ab66-5d2447a9ebf2
    url_split = agent['url'].split('/')
    agent['id'] = '/' + url_split[-2] + '/' + url_split[-1]

    return agent


# Check that the driver's current window and url are the same as the agent's information
def check_window_url(driver=None, agent=None, window_handle=None, url=None):
    if driver is None: driver = DEFAULT_DRIVER

    if agent is not None:
        if agent['window_handle'] is not None and driver.current_window_handle != agent['window_handle']:
            driver.switch_to.window(agent['window_handle'])
        if agent['url'] is not None and driver.current_url != agent['url']:
            driver.get(agent['url'])
    else:
        if window_handle is not None:
            if isinstance(window_handle, int): window_handle = driver.window_handles[window_handle]
            driver.switch_to.window(window_handle)
        if url is not None:
            driver.get(url)


# send message
def send_message(driver=None, agent=None, window_handle=None, url=None, msg=''):
    if driver is None: driver = DEFAULT_DRIVER

    # if the agent already exists, check the window handle and the url
    check_window_url(driver=driver, agent=agent, window_handle=window_handle, url=url)

    # find a text input area, and input a message
    text_area = driver.find_element(By.ID, 'prompt-textarea')

    # If msg contains '\n' characters, change '\n' to Shift+Enter.
    for m in msg.split('\n'):
        text_area.send_keys(m)
        text_area.send_keys(Keys.SHIFT + Keys.ENTER)

    # wait a second.
    time.sleep(1)

    # click a send button
    send_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="send-button"]')
    while not send_button.is_enabled:
        time.sleep(1)
    send_button.click()


def send_image(driver=None, agent=None, window_handle=None, url=None, image_path=None, image_paths=None):
    if driver is None: driver = DEFAULT_DRIVER
    
    # if the agent already exists, check the window handle and the url
    check_window_url(driver=driver, agent=agent, window_handle=window_handle, url=url)

    # Find file input element
    file_input = driver.find_element(By.CSS_SELECTOR, "input[type=file]")

    if image_path is not None:
        file_input.send_keys(image_path)
        time.sleep(1)
    if image_paths is not None:
        #file_input.send_keys(image_paths)
        #time.sleep(1)
        for image_path in image_paths:
            file_input.send_keys(image_path)
            time.sleep(1)


def stop_program(agent, error_text):
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


# get conversations and status
def update_conversations(driver=None, agent=None, window_handle=None, url=None):
    if driver is None: driver = DEFAULT_DRIVER
    check_window_url(driver=driver, agent=agent, window_handle=window_handle, url=url)

    # check a status
    status = check_status(driver=driver, agent=agent, window_handle=window_handle, url=url)

    # Get conversation elements
    conversation_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid^="conversation-turn-"]')

    # if there is any conversation, then return "Not Started"
    if len(conversation_elements) == 0: return [], AgentStatus.NOT_STARTED

    # Extracting text from elements.
    try:
        conversations = []
        for conversation_element in conversation_elements:
            try:
                conversation = conversation_element.text
            except:
                conversation = ''
            
            conversations.append(conversation)

    except Exception as e:
        print('conversations error')
        print(e)
    

    # if agent is not None, then update conversations of agent
    if agent is not None:
        agent['conversations'] = conversations
        agent['status'] = status

    return conversations, status


# get message
def get_message(driver=None, agent=None, window_handle=None, url=None, turn=-1):
    if driver is None: driver = DEFAULT_DRIVER
    check_window_url(driver=driver, agent=agent, window_handle=window_handle, url=url)

    status = AgentStatus.RESPONDING
    while status == AgentStatus.RESPONDING:
        conversations, status = update_conversations(driver=driver, agent=agent, window_handle=window_handle, url=url)
        agent['lock'].release()
        time.sleep(1)
        agent['lock'].acquire()
        time.sleep(1)
    
    # customized
    timeout = 600
    start_time = time.time()
    while time.time() - start_time < timeout:
        conversations, status = update_conversations(driver=driver, agent=agent, window_handle=window_handle, url=url)
        error_flag = False
        if len(conversations) > 0:
            if 'ChatGPT' not in conversations[-1]: error_flag = True
            if '#problem: \\' not in conversations[-1]: error_flag = True
            if '#evalf_value' not in conversations[-1]: error_flag = True
        
        if not error_flag: break

