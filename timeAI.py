import openai
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

openai.api_base = "http://localhost:1234/v1"
openai.api_key = "not-needed"


messages = [{"role": "user", "content": "Can you check what is the time in Singapore?"}]
response = client.chat.completions.create(
    model="jeffrey-fong/invoker-13b",
    messages=messages,
    functions=[
        {
            "name": "get_time",
            "description": "Get the current time",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. New York City, NY"
                    },
                    "format": {
                    "type": "string",
                    "enum": ["12-hour", "24-hour"]
                    }
                },
                "required": ["location"]
            }
        }
    ]
)

print(response)
response_message = response["choices"][0]["message"]

if response_message.get("function_call"):
  available_functions = {"get_time": get_time}
  function_name = response_message["function_call"]["name"]
  function_to_call = available_functions[function_name]
  function_args = json.loads(response_message["function_call"]["arguments"])
  function_response = function_to_call(
      location=function_args.get("location"),
      unit=function_args.get("format"),
  )
  messages.append(response_message)
  messages.append(
      {
          "role": "function",
          "name": function_name,
          "content": function_response,
      }
  )
  second_response = openai.ChatCompletion.create(
      model="jeffrey-fong/invoker-13b",
      messages=messages,
  )
  print(second_response["choices"][0]["message"])