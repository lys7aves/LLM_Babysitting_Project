import os
import openai
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
 
import logging  
  
# Configure logging  
logging.basicConfig(level=logging.INFO)  
  
# Error callback function
def log_retry_error(retry_state):  
    logging.error(f"Retrying due to error: {retry_state.outcome.exception()}")  

DEFAULT_CONFIG = {
    "engine": "devgpt4-32k",
    "temperature": 0.0,
    "max_tokens": 5000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stop": None
}

class OpenAIWrapper:
    def __init__(self, config = DEFAULT_CONFIG, system_message=""):
        # TODO: set up your API key with the environment variable OPENAIKEY
        openai.api_key = os.environ.get("OPENAI_API_KEY")      

        if os.environ.get("USE_AZURE")=="True":
            print("using azure api")
            openai.api_type = "azure"
        openai.api_base = os.environ.get("API_BASE")
        openai.api_version = os.environ.get("API_VERSION")

        self.config = config
        print("api config:", config, '\n')

        # count total tokens
        self.completion_tokens = 0
        self.prompt_tokens = 0

        # system message
        self.system_message = system_message # "You are an AI assistant that helps people find information."
        self.client = OpenAI()

    # retry using tenacity
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), retry_error_callback=log_retry_error)
    def completions_with_backoff(self, **kwargs):
        # print("making api call:", kwargs)
        print()
        print("====================================")
        print(f"messages : P{kwargs['messages']}\n")

        # print(f"model    : {kwargs['model']}\n")
        # print(f"engine   : {kwargs['engine']}\n")
        # print(f"stream   : {kwargs['stream']}\n")
        print("====================================")
        print()
        #res = openai.ChatCompletion.create(**kwargs)
        res = self.client.chat.completions.create(
            messages = kwargs['messages'],
            model='gpt-4',
            temperature=kwargs['temperature'],
            max_tokens=kwargs['max_tokens'],
        )
        return res
    def run(self, prompt, n=1, system_message=""):
        """
            prompt: str
            n: int, total number of generations specified
        """
        try:
            # overload system message
            if system_message != "":
                sys_m = system_message
            else:
                sys_m = self.system_message
            if sys_m != "":
                print("adding system message:", sys_m)
                messages = [
                    {"role":"system", "content":sys_m},
                    {"role":"user", "content":prompt}
                ]
            else:
                messages = [
                    {"role":"user","content":prompt}
                ]
            text_outputs = []
            raw_responses = []
            while n > 0:
                cnt = min(n, 10) # number of generations per api call
                n -= cnt
                print(f"=============================   generating {cnt} responses ...")
                res = self.completions_with_backoff(messages=messages, n=cnt, **self.config)
                print(f"=============================   done generating {cnt} responses ...")
                print()
                print(f"============================  response: {res}")
                print(f"============================  text_outputs before extending: {text_outputs}")
                # add to text outputs
                text_outputs.extend([choice.message.content for choice in res.choices])
                # add prompt to log
                print(f"============================  text_outputs after expending: {text_outputs}")

                response_data = {
                    "response": res,
                    "prompt": prompt
                }

                if sys_m != "":
                    response_data["system_message"] = sys_m

                # Now you can work with `response_data` dictionary
                raw_responses.append(response_data)

                # Accessing usage data from the ChatCompletion object
                self.completion_tokens += res.usage.completion_tokens
                self.prompt_tokens += res.usage.prompt_tokens

            return text_outputs, raw_responses
        except Exception as e:
            print("an error occurred:", e)
            return [], []

    def compute_gpt_usage(self):
        engine = self.config["engine"]
        if engine == "gpt-4":
            cost = self.completion_tokens / 1000 * 0.12 + self.prompt_tokens / 1000 * 0.06
        else:
            cost = 0 # TODO: add custom cost calculation for other engines
        return {"completion_tokens": self.completion_tokens, "prompt_tokens": self.prompt_tokens, "cost": cost}