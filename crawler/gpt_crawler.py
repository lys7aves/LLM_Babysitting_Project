# Last updated: 2023. 11. 23.

# C:\Program Files\Google\Chrome\Application> chrome.exe --remote-debugging-port=9222

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from enum import Enum

class AgentStatus(Enum):
    RESPONDING = 'Responding'
    WAITING = 'Waiting'
    NOT_STARTED = 'Not Started'

DEFAULT_DRIVER = None

# Connect to a chrome browser
def connect_browser():
    # Connect to a Chrome browser that is already running
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    chrome_driver_path = 'chromedriver_114.0.5735.90/chromedriver.exe' 
    chrome_options.add_extension(chrome_driver_path)

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)

    global DEFAULT_DRIVER
    DEFAULT_DRIVER = driver

    return driver


def disconnect_browser(driver=None):
    if driver is None: driver = DEFAULT_DRIVER

    driver.quit()


def start_new_chat(driver=None, agent_name='', first_msg=' ', first_image=None, window_handle=None, model=None):
    if driver is None: driver = DEFAULT_DRIVER

    # if you know window handle, then switch to the window
    # else get a current window handle
    if window_handle is not None:
        # if you only know the number of window, then find the window handle
        if isinstance(window_handle, int): window_handle = driver.window_handles[window_handle]
        driver.switch_to.window(window_handle)
    else:
        window_handle = driver.current_window_handle

    gpt_url = 'https://chat.openai.com/'
    if model == 'gpt-3.5': gpt_url += '?model=text-davinci-002-render-sha'
    if model == 'gpt-4': gpt_url += '?model=gpt-4'
    driver.get(gpt_url)
    
    time.sleep(3)

    # send the first message, and get a response
    if first_image is not None: send_image(driver=driver, image_path=first_image)
    send_message(driver=driver, msg=first_msg)
    response = get_message(driver=driver)
    url = driver.current_url

    agent_information = {
        'name': agent_name,
        'url': url,
        'window_handle': window_handle,
        'conversations': [first_msg, response],
        'status': AgentStatus.WAITING
    }

    return agent_information


# Check that the driver's current window and url are the same as the agent's information
def check_window_url(driver=None, agent=None, window_handle=None, url=None):
    if driver is None: driver = DEFAULT_DRIVER
    if agent is not None:
        if driver.current_window_handle != agent['window_handle']:
            driver.switch_to.window(agent['window_handle'])
        if driver.current_url != agent['url']:
            driver.get(agent['url'])
    else:
        if window_handle is not None:
            if isinstance(window_handle, int): window_handle = driver.window_handles[window_handle]
            driver.switch_to.window(window_handle)
        if url is not None: driver.get(url)


# send message
def send_message(driver=None, agent=None, window_handle=None, url=None, msg=' '):
    if driver is None: driver = DEFAULT_DRIVER

    # if the agent already exists, check the window handle and the url
    check_window_url(driver=driver, agent=agent, window_handle=window_handle, url=url)

    # if msg has some '\n', then replace it to ' '
    msg = msg.replace('\n', ' ')

    # find a text input area, and input a message
    text_area = driver.find_element(By.ID, 'prompt-textarea')
    text_area.send_keys(msg)

    # click a send button
    send_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="send-button"]')
    send_button.click()


def send_image(driver=None, agent=None, window_handle=None, url=None, image_path=None):
    if driver is None: driver = DEFAULT_DRIVER
    
    # if the agent already exists, check the window handle and the url
    check_window_url(driver=driver, agent=agent, window_handle=window_handle, url=url)

    file_input = driver.find_element(By.CSS_SELECTOR, "input[type=file]")
    file_input.send_keys(image_path)

    time.sleep(2)


# check that gpt has finished responding
def is_response_complete(conversation):
    # Use the presence or absence of the right icon
    elements = conversation.find_elements(By.XPATH, './div/div/div[2]/div/div[2]/div/*')

    if len(elements) == 1: return False
    if len(elements) == 2: return True


# get conversations and status
def get_conversations(driver=None, agent=None, window_handle=None, url=None):
    if driver is None: driver = DEFAULT_DRIVER

    check_window_url(driver=driver, agent=agent, window_handle=window_handle, url=url)

    conversations = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid]')

    # if there is any conversation, then return "Not Started"
    if len(conversations) == 0: return [], AgentStatus.NOT_STARTED

    # check a status
    if is_response_complete(conversation=conversations[-1]) or len(conversations)%2 == 1:
        status = AgentStatus.WAITING
    else:
        status = AgentStatus.RESPONDING

    # convert url to text
    conversations = [conversation.text for conversation in conversations]

    # if agent is not None, then update conversations of agent
    if agent is not None:
        agent['conversations'] = conversations
        agent['status'] = status

    return conversations, status


# get message
def get_message(driver=None, agent=None, window_handle=None, url=None, turn=-1, waiting_time=1):
    if driver is None: driver = DEFAULT_DRIVER

    conversations = []
    status = AgentStatus.RESPONDING
    error = False
    while (turn == -1 or turn == len(conversations)-1) and status == AgentStatus.RESPONDING and not error:
        try:
            conversations, status = get_conversations(driver=driver, agent=agent, window_handle=window_handle, url=url)
            error = False
        except Exception:
            error = True
        time.sleep(waiting_time)
    
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
        

# not yet
def delete_all_chat(driver):
    driver.get('https://chat.openai.com/')
    time.sleep(1)


# This is the test function
def test_crawling():
    print('Setting up configuration...')

    driver = connect_browser()

    #print_window_handles()

    # This is my window handle during the test time. You can just write numbers and test them.


    agent_name = 'ChatGPT'
    first_msg = 'Solve it'
    first_image = r'C:\Users\SAMSUNG\OneDrive\바탕 화면\Lecture\2023-2\2023-2 Natural Language Processing (001)\project\LLM_Babysitting_Project\formula_recognition\data\random_problems_v1\problem1.png'
    window_handle = 'D428C9864603DD6539A6E1D6A919A585'
    model = 'gpt-4'
    agent = start_new_chat(driver=driver, agent_name=agent_name, first_msg=first_msg, first_image=first_image, window_handle=window_handle, model=model)

    print('Ready for conversation!')
    print()

    while True:
        input_msg = input('you : ')

        #send_image(agent=agent, image_path=r'C:\Users\LeeYuseop\OneDrive\바탕 화면\Lecture\2023-2\2023-2 Natural Language Processing (001)\project\data\sudoku\sudoku1.png')
        send_message(agent=agent, msg=input_msg)

        response = get_message(agent=agent)

        print(agent_name, ':', response)

    

if __name__ == "__main__":
    test_crawling()

    print('finish')