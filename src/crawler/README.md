# gpt_crawler

## Requirements



## Pre-work

1. Open Chrome browser with 9222 port
   1. cd C:\Program Files\Google\Chrome\Application
   2. chrome.exe --remote-debugging-port=9222
2. Open sufficient number of tabs.



## Functions

- connect_browser
  - It must be called once at first.
  - The return value is driver, but it does not have to be saved.
- disconnect_browser
  - parameter: driver
- start_new_chat
  - parameters
    - driver
    - agent_name
    - first_msg: It's good to have it.
    - tab_handle
      - If you know the tab handle, you can put it in.
      - Or you can put it in numbers. However, numbers are not in the order of opening the tab.
    - model
      - 'gpt-3.5'
      - 'gpt-4'
      - None
  - returns
    - agent_information: dictionary
      - 'name': agent_name
      - 'url': chatGPT unique url
      - 'tab_handle': tab unique handle
      - 'conversations': a list of conversations
      - 'status': Manage with AgentStatus class('Responding', 'Waiting', 'Not Started')
- send_message
  - parameters
    - Not required: driver, tab_handle, url
    - Recomended: agent, msg
  - No return
- send_image
  - incomplete
  - parameters
    - Not required: driver, tab_handle, url
    - Recommended: agent, image_path
  - No return
- get_message
  - parameters
    - Not required: driver, tab_handle, url
    - Recommended: agent
    - Option
      - turn: turn of the conversation you want to know (starting with number 0, getting the last response if -1(default))
      - waiting_time: wait time between response checks



