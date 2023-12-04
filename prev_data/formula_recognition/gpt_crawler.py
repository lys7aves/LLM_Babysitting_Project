# Last updated: 2023. 11. 28. 16:08

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


def set_agent(agent=None, model=None, name=None, url=None, _id=None, window_handle=None, conversations=[], status=AgentStatus.FREE, lock=LOCK):
    if agent is None:
        agent = {
            'model': None,
            'name': 'chatgpt',
            'url': None,
            'id': None,
            'window_handle': None,
            'conversations': [],
            'status': None,
            'lock': None
        }
    
    if model is not None: agent['model'] = model
    if name is not None: agent['name'] = name
    if url is not None: agent['url'] = url
    if _id is not None: agent['id'] = _id
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
    #print('set agent:', agent)

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
        #print('send image!', first_images)

    ## Send the first_msg
    send_message(driver=driver, window_handle=window_handle, msg=first_msg)
    #print('send message!')
    time.sleep(1)

    ## Get the respond
    get_message(driver=driver, agent=agent, turn=1)
    #print('get mesage!')


    check_window_url(driver=driver, window_handle=window_handle)
    # Get a current url. This is a chatGPT's unique url.
    agent['url'] = driver.current_url
    # We can get a unique id from the url. For example in https://chat.openai.com/c/364f93f1-c1db-471a-ab66-5d2447a9ebf2, we can get /c/364f93f1-c1db-471a-ab66-5d2447a9ebf2
    '''url_split = agent['url'].split('/')
    agent['id'] = '/' + url_split[-2] + '/' + url_split[-1]'''

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
            # I don't know why it is duplicate, so before to upload files, delete all of the files.
            delete_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[class="absolute right-1 top-1 -translate-y-1/2 translate-x-1/2 rounded-full border border-white bg-gray-500 p-0.5 text-white transition-colors hover:bg-black hover:opacity-100 group-hover:opacity-100 md:opacity-0"]')
            for delete_button in delete_buttons:
                delete_button.click()
                time.sleep(1)

            file_input.send_keys(image_path)
            time.sleep(1)


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
        print(time.strftime('[%H:%M:%S]'), f"agent #{agent['id']} releases lock")
        agent['lock'].release()
        time.sleep(1)
        agent['lock'].acquire()
        print(time.strftime('[%H:%M:%S]'), f"agent #{agent['id']} acquires lock")
        time.sleep(1)

    # customized
    timeout = 600
    start_time = time.time()
    while time.time() - start_time < timeout:
        conversations, status = update_conversations(driver=driver, agent=agent, window_handle=window_handle, url=url)
        error_flag = False
        if len(conversations) == 0: error_flag = True
        else:
            if 'ChatGPT' not in conversations[-1]: error_flag = True
            #if '#problem: \\' not in conversations[-1]: error_flag = True
            if '#evalf_value' not in conversations[-1]: error_flag = True
        
        if not error_flag: break

        print(time.strftime('[%H:%M:%S]'), f"agent #{agent['id']} releases lock")
        agent['lock'].release()
        time.sleep(1)
        agent['lock'].acquire()
        print(time.strftime('[%H:%M:%S]'), f"agent #{agent['id']} acquires lock")
        time.sleep(1)

    print(time.strftime('[%H:%M:%S]'), f"agent #{agent['id']}'s conversations:", conversations, status)
    if status != AgentStatus.WAITING:
        print(status.value)

    # if there is any conversation, then return "Not Started"
    if status == AgentStatus.NOT_STARTED: return status.value

    try:
        return conversations[turn]
    except Exception:
        return f'No {turn}th conversation'
    

def print_window_handles(driver=None):
    if driver is None: driver = DEFAULT_DRIVER

    # get a current window handle and all of window handles
    window_handles = driver.window_handles
    current_window_handle = driver.current_window_handle

    print()
    print("current window handle:", current_window_handle)
    print("current_window_url:", driver.current_url)

    # print all of window handles and each url
    print("window_handles:")
    for window_handle in window_handles:
        # switch the window to get the url of the corresponding window
        driver.switch_to.window(window_handle)
        # current_url = None if the window is not connected to any url
        try:
            current_url = driver.current_url
        except Exception:
            current_url = None

        print("-", window_handle, current_url)
    print()

    # Return to the original window
    driver.switch_to.window(current_window_handle)
        

# Delete agent from the chatGPT page.
# If the agent is None, then delete all of the agent.
def delete_agent(driver=None, agent=None, window_handle=None):
    if driver is None: driver = DEFAULT_DRIVER
    check_window_url(driver=driver, agent=agent, window_handle=window_handle)
    
    # Go to the chatGPT page
    url = "https://chat.openai.com/"
    driver.get(url)

    # Wait until the left bar appears.
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="group relative active:opacity-90"]'))
    )

    # Get chat elements
    cnt=0
    chat_elements = driver.find_elements(By.CSS_SELECTOR, 'div[class="group relative active:opacity-90"]')
    for chat_element in chat_elements:
        cnt += 1
        if cnt > 10: break
        chat_url = chat_element.find_element(By.XPATH, './*').get_attribute('href')

        if agent is None or chat_url == agent['url']:
            # Sometimes it doesn't work. so try 10 times.
            for i in range(10):
                try:
                    chat_element.click()
                    time.sleep(1)

                    button = chat_element.find_element(By.TAG_NAME, 'button')
                    button.click()
                    time.sleep(1)

                    menuitems = driver.find_elements(By.CSS_SELECTOR, 'div[role="menuitem"]')
                    menuitems[2].click()
                    time.sleep(1)

                    delete_button = driver.find_element(By.CSS_SELECTOR, 'button[class="btn relative btn-danger"]')
                    delete_button.click()
                    time.sleep(1)

                    break
                except:
                    time.sleep(1)

            agent['status'] = AgentStatus.FREE


# This is the test function
def test_crawling():
    global DEFAULT_DRIVER

    driver = connect_browser()
    DEFAULT_DRIVER = driver

    # If you don't know window handle informations, then you can use this function.
    print_window_handles()

    first_msg = "Read the mathematical expression from the image and represent it in LaTeX syntax."
    first_msg = "This message\ninvolves\nnew line character."
    print(first_msg)
    first_image = r"C:\Users\SAMSUNG\OneDrive\바탕 화면\Lecture\2023-2\2023-2 Natural Language Processing (001)\project\LLM_Babysitting_Project\formula_recognition\data\random_problems_v1\problem2.png"
    #first_image = None
    window_handle = "15B0E65320786235702C99D0E052DC23"
    #window_handle = "FDB349224C84327A6F4A8A8CFF9CB800"
    #window_handle = "ED3227B313044425861E668679444408"      # desktop yuseop window
    model = "gpt-4"
    model = "gpt-3.5"
    #agent = start_new_chat(driver=driver, first_msg=first_msg, first_image=first_image, window_handle=window_handle, model=model)

    agent = {
        'url': 'https://chat.openai.com/c/1085b077-a3f4-4803-aced-3a90a4452869'
    }
    delete_agent(driver=driver, agent=agent, window_handle=window_handle)

    

if __name__ == "__main__":
    test_crawling()

    print('finish')