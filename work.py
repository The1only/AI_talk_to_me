import requests

def wikipedia_search(query):
    url = f"https://en.wikipedia.org/wiki/{query}" 
    response = requests.get(url)
    if response.status_code == 200:
                return response.text
                else:
                return None
    
if __name__ == "__main__":
    query = "Elon Musk"
    result = wikipedia_search(query)
    if result:
        print(result)
    else:
        print("No result found.")

# chat2 = [{"role": "system", \
#     "content": "You are a function calling AI model. You are provided with function signatures within <tools></tools> XML tags. \
#     You may call one or more functions to assist with the user query. Don't make assumptions about what values to plug into functions. \
#     Here are the available tools: <tools> \
#     {'type': 'function', 'function': {'name': 'get_stock_fundamentals', 'description': 'get_stock_fundamentals(symbol: str) -> dict - Get fundamental data for a given stock symbol using yfinance API.\n\n    Args:\n    symbol (str): The stock symbol.\n\n    Returns:\n    dict: A dictionary containing fundamental data.', 'parameters': {'type': 'object', 'properties': {'symbol': {'type': 'string'}}, 'required': ['symbol']}}}  </tools>  Use the following pydantic model json schema for each tool call you will make: {'title': 'FunctionCall', 'type': 'object', 'properties': {'arguments': {'title': 'Arguments', 'type': 'object'}, 'name': {'title': 'Name', 'type': 'string'}}, 'required': ['arguments', 'name']} \
#     For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows: \
#     <tool_call> \
#     {'arguments': <args-dict>, 'name': <function-name>} \
#     </tool_call>"},
#     {"role": "user", "content": "Fetch the stock fundamentals data for Tesla (TSLA)"}]


# client = OpenAI(base_url="http://150.136.107.40:8500/v1", api_key="not-needed")

#conversation=tokenizer.apply_chat_template(chat, tokenize=False)

# completion = client.chat.completions.create( model="local-model", messages=chat, temperature=0.7 )
# assistant_reply = completion.choices[0].message.content
# print(assistant_reply)


# # Code to inference Hermes with HF Transformers
# # Requires pytorch, transformers, bitsandbytes, sentencepiece, protobuf, and flash-attn packages

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import LlamaTokenizer, MixtralForCausalLM
import bitsandbytes #, flash_attn

#tokenizer = LlamaTokenizer.from_pretrained('NousResearch/Hermes-2-Pro-Mistral-7B', trust_remote_code=True)
# model = MistralForCausalLM.from_pretrained(
#     "NousResearch/Hermes-2-Pro-Mistral-7B",
#     torch_dtype=torch.float16,
#     device_map="auto",
#     load_in_8bit=False,
#     load_in_4bit=True,
#     use_flash_attention_2=True
# )

prompts = [
    """<|im_start|>system
You are a sentient, superintelligent artificial general intelligence, here to teach and assist me.<|im_end|>
<|im_start|>user
Write a short story about Goku discovering kirby has teamed up with Majin Buu to destroy the world.<|im_end|>
<|im_start|>assistant""",
    ]

for chat in prompts:
    print(chat)
    print("...")
 #   input_ids = tokenizer(chat, return_tensors="pt").input_ids.to("cuda")
#    generated_ids = model.generate(input_ids, max_new_tokens=750, temperature=0.8, repetition_penalty=1.1, do_sample=True, eos_token_id=tokenizer.eos_token_id)
#    response = tokenizer.decode(generated_ids[0][input_ids.shape[-1]:], skip_special_tokens=True, clean_up_tokenization_space=True)
#    print(f"Response: {input_ids}")



# import openai
# import json

# client = openai.OpenAI(base_url="http://150.136.107.40:8500/v1", api_key="not-needed")


# # Example dummy function hard coded to return the same weather
# # In production, this could be your backend API or an external API
# def get_current_weather(location, unit="fahrenheit"):
#     """Get the current weather in a given location"""
#     if "tokyo" in location.lower():
#         return json.dumps({"location": "Tokyo", "temperature": "-10", "unit": "celsius"})
#     elif "san francisco" in location.lower():
#         return json.dumps({"location": "San Francisco", "temperature": "-72", "unit": "fahrenheit"})
#     elif "paris" in location.lower():
#         return json.dumps({"location": "Paris", "temperature": "-22", "unit": "celsius"})
#     else:
#         return json.dumps({"location": location, "temperature": "unknown"})

# def run_conversation():
#     # Step 1: send the conversation and available functions to the model
#     messages = [{"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris?"}]
#     tools = [
#         {
#             "type": "function",
#             "function": {
#                 "name": "get_current_weather",
#                 "description": "Get the current weather in a given location",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "location": {
#                             "type": "string",
#                             "description": "The city and state, e.g. San Francisco, CA",
#                         },
#                         "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
#                     },
#                     "required": ["location"],
#                 },
#             },
#         }
#     ]
#     response = client.chat.completions.create(
#         model="local-model",
#         messages=messages,
#         tools=tools,
#         tool_choice="auto",  # auto is default, but we'll be explicit
#     )
#     response_message = response.choices[0].message
#     tool_calls = response_message.tool_calls
#     # Step 2: check if the model wanted to call a function
#     if tool_calls:
#         # Step 3: call the function
#         # Note: the JSON response may not always be valid; be sure to handle errors
#         available_functions = {
#             "get_current_weather": get_current_weather,
#         }  # only one function in this example, but you can have multiple
#         messages.append(response_message)  # extend conversation with assistant's reply
#         # Step 4: send the info for each function call and function response to the model
#         for tool_call in tool_calls:
#             function_name = tool_call.function.name
#             function_to_call = available_functions[function_name]
#             function_args = json.loads(tool_call.function.arguments)
#             function_response = function_to_call(
#                 location=function_args.get("location"),
#                 unit=function_args.get("unit"),
#             )
#             messages.append(
#                 {
#                     "tool_call_id": tool_call.id,
#                     "role": "tool",
#                     "name": function_name,
#                     "content": function_response,
#                 }
#             )  # extend conversation with function response
#         second_response = client.chat.completions.create(
#             model="local-model",
#             messages=messages,
#         )  # get a new response from the model where it can see the function response
#         return second_response
    
#     return response.choices[0].message
    
# print(run_conversation())


import requests

url = 'https://en.wikipedia.org/wiki/Elon_Musk' 
response = requests.get(url)

import re

extracted_info = re.search('<title>Elon_Musk</title>.*.?<div class='mw-headline'.*?<h1 id='mw-headline'>.*?<span>(.*?)</span>.*?</h1>.*?<div class='mw-body'.*?<div class='mw-parser-output'>.*?<p>(.*?)</p>.*.?</div>', response.text) 

file = open('elon_musk_info.txt', 'w')
file.write(extracted_info.group(1) + ' - ' + extracted_info.group(2))
file.close()


import requests

url = "https://en.wikipedia.org/wiki/Elon_Musk" 
response = requests.get(url)

import re
extracted_info = re.search("<title>Elon_Musk</title>.*.?<div class=\"mw-headline\".*?<h1 id=\"mw-headline\">.*?<span>(.*?)</span>.*?</h1>.*?<div class=\"mw-body\".*?<div class=\"mw-parser-output\">.*?<p>(.*?)</p>.*.?</div>", response.text) 

file = open("elon_musk_info.txt", "w")
file.write(extracted_info.group(1) + " - " + extracted_info.group(2))
file.close()

# from openai import OpenAI
# import openai
# import warnings
# import ast
# from pydantic import create_model
# import inspect, json
# from inspect import Parameter
# import datetime
# from pychatml.llama2_converter import Llama2


# def get_time():
#     return datetime.datetime.now().strftime("%M")
# #------------------------------------------------
# # Point to the local server
# client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
# warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
# openai.api_base = "http://localhost:1234/v1"
# openai.api_key = "not-needed"

# #------------------------------------------------
# my_name = "Terje"
# input_text = "What the factorial of 3?"
# function_check = {"factorial", "sums", "gpt_python", "solve_sudoku"}
# fact_value = 3

# messages = [
#     {"role": "system", "content": "You are Hermes 2."},
#     {"role": "user", "content": "Hello, who are you?"}
# ]
# gen_input = tokenizer.apply_chat_template(message, return_tensors="pt")
# model.generate(**gen_input)

# PROMPT = """[INST] You are an external 'function' calling AI model. You may call one or more functions to assist with the user query. [/INST] OK, I will do that.
# [INST] How can the user write prompt that make an LLM use an external 'function' to find the answer? [/INST]"""


# PROMPT2 = """<|im_start|>system
# You are a function calling AI model. You are provided with function signatures within <tools></tools> XML tags. 
# You may call one or more functions to assist with the user query. Don't make assumptions about what values to plug into functions. 
# Here are the available tools: <tools> {'type': 'function', 'function': {'name': 'get_time', 'description': 'get current local time -> int - Will return the current time.\n\n  Returns:\n   int: The current minute.'}}  </tools> 
# Use the following pydantic model json schema for each tool call you will make: {'title': 'FunctionCall', 'type': 'object'} 
# For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows:
# <tool_call>{'arguments': <args-dict>, 'name': <function-name>}</tool_call><|im_end|>
# <|im_start|>user
# What time is it<|im_end|>"""


# converter = Llama2()

# completion = client.chat.completions.create( model="local-model", messages=converter.to_chatml(PROMPT), temperature=0.7)
# assistant_reply = completion.choices[0].message.content

# print(f"KITT: {assistant_reply}")
