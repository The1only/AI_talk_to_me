from openai import OpenAI
import openai
import warnings
import ast
from pydantic import create_model
import inspect, json
from inspect import Parameter

#------------------------------------------------
# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "not-needed"

#------------------------------------------------
my_name = "Terje"
input_text = "What the factorial of 3?"
function_check = {"factorial", "sums", "gpt_python", "solve_sudoku"}
fact_value = 3

#------------------------------------------------
def run(code):
    print("Run: "+code)
    tree = ast.parse(code)
    last_node = tree.body[-1] if tree.body else None
    
    # If the last node is an expression, modify the AST to capture the result
    if isinstance(last_node, ast.Expr):
        tgts = [ast.Name(id='_result', ctx=ast.Store())]
        assign = ast.Assign(targets=tgts, value=last_node.value)
        tree.body[-1] = ast.fix_missing_locations(assign)

    ns = {}
    exec(compile(tree, filename='<ast>', mode='exec'), ns)
    return ns.get('_result', None)


run("""
x = 2
y = 5
x+y
""")


def call_func(ask_function):
    func = ask_function.choices[0].message.function_call
    print(func)
    if func.name not in function_check: 
        return print(f"Not allowed: {func.name}")
    fun = globals()[func.name]
    #print(func.arguments)
    result = fun(**json.loads(func.arguments))
    return result

def gpt_python(code:str):
    print("gpt_python: " + code)
    "Return result of executing python 'code'. If execution is not allowed returns '_NOT_ALLOWED_'"
    allowed = input(f"Run the code?\n'''\n{code}\n'''\n")
    if allowed.lower()!="y":
        return "_NOT_ALLOWED_"
    return run(code)

def gpt_func(user, system=None, model="local-model", **kwargs):
    msgs = []
    if system: msgs.append({"role": "function", "name": "gpt_python", "content": system})
#    if system: msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": user})
    print(msgs)
#    return client.chat.completions.create(model=model, messages=msgs, **kwargs)
#    return client.chat.completions.create(model=model, messages=msgs,temperature=0.7)
    x = client.chat.completions.create(model=model, messages=msgs,temperature=0.7)
    print("Ansver one:    ")
    print(x)
    return x

def schema(f):
    kw = {n:(o.annotation, ... if o.default==Parameter.empty else o.default)
          for n,o in inspect.signature(f).parameters.items()}
    s = create_model(f'Input for `{f.__name__}`', **kw).model_json_schema()
    return dict(name=f.__name__, description=f.__doc__, parameters=s)

#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------
print("Bootstrapping functions...")

ask_function_python = gpt_func(f"What is {fact_value} factorial?",system = "Use python for any required computations.",functions=[schema(gpt_python)],temperature=0.7)
x = ask_function_python.choices[0].message.content
print(x)

result_var = str(call_func(ask_function_python))
print(f"TESTTEST:  {fact_value}! = {result_var}")

conversation = [
        {"role": "system", "content": "You are Mary, a function calling assistant chatbot. \
        You are provided with function signatures within <tools></tools> XML tags. \
        You may call one or more functions to assist with the user query. \
         Don't make assumptions about what values to plug into functions. \
        Here are the available tools: <tools> \
        {'type': 'function', 'function': {'name': 'get_number', 'description': 'get_number(symbol: real) -> list - Get the next number in a sequence.\n\n    Args:\n    number (list): The list on nymbers.\n\n    Returns:\n    real: The next number in the list.', \
        'parameters': {'type': 'object', 'properties': {'symbol': {'type': 'list'}}, 'required': ['symbol']}}}  </tools> \
        Use the following pydantic model json schema for each tool call you will make: \
        {'title': 'FunctionCall', 'type': 'object', 'properties': {'arguments': {'title': 'Arguments', 'type': 'object'}, 'name': {'title': 'Name', 'type': 'string'}}, 'required': ['arguments', 'name']} \
        For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows: \
        <tool_call> \
        {'arguments': <args-list>, 'name': <function-name>} \
        </tool_call> \
        My name is "+my_name+", the human and user. Your role is to assist the human, who is known as "+my_name+". \
        Respond concisely and accurately, maintaining a friendly, respectful, and professional tone. \
        Emphasize honesty, candor, and precision in your responses."},
        {"role": "function", "name": "gpt_python", "content": result_var}
    ]

completion = client.chat.completions.create( model="local-model", messages=conversation, temperature=0.7)
assistant_reply = completion.choices[0].message.content

print(f"KITT: {assistant_reply}")


from pychatml.llama2_converter import Llama2

PROMPT = """[INST] Hi, how are you? [/INST] Good thanks!
[INST] Can you help me with this math program? [/INST]"""

PROMPT = """<|im_start|>system
You are a function calling AI model. You are provided with function signatures within <tools></tools> XML tags. 
You may call one or more functions to assist with the user query. 
Don't make assumptions about what values to plug into functions. 
Here are the available tools: <tools> 
{'type': 'function', 'function': {'name': 'get_stock_fundamentals', 'description': 'get_stock_fundamentals(symbol: str) -> dict - Get fundamental data for a given stock symbol using yfinance API.\n\n    Args:\n    symbol (str): The stock symbol.\n\n    Returns:\n    dict: A dictionary containing fundamental data.', 'parameters': {'type': 'object', 'properties': {'symbol': {'type': 'string'}}, 'required': ['symbol']}}}  </tools> 
Use the following pydantic model json schema for each tool call you will make: 
{'title': 'FunctionCall', 'type': 'object', 'properties': {'arguments': {'title': 'Arguments', 'type': 'object'}, 'name': {'title': 'Name', 'type': 'string'}}, 'required': ['arguments', 'name']} 
For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows:
<tool_call>
{'arguments': <args-dict>, 'name': <function-name>}
</tool_call><|im_end|>"""

converter = Llama2()

converter.to_chatml(PROMPT)
