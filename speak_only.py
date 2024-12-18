#------------------------------------------------

# Add embedding using embedding model instructor, chroma eller influx
# HKUMlp large

# arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32S3 Blink 
# arduino-cli upload -p /dev/tty.usbmodem11401   --fqbn  esp32:esp32:XIAO_ESP32S3 Blink

# Step 1: Import necessary libraries and modules
import json
import warnings
import pyaudio
import wave
import whisper
#import openai
from openai import OpenAI
from pynput import keyboard
import os
import pyttsx3
from gtts import gTTS
import tkinter as tk
from tkinter import simpledialog
import time
import struct
import math
from pygame import mixer, _sdl2 as devices
import wikipedia
import webbrowser
import datetime
import pyjokes
import language_text as lang

#------------------------------------------------
#------------------------------------------------

LANGUAGE = 'en_US'
#LANGUAGE = 'nb_NO'

RUN_QUIET = True
DO_NOT_SPEAK = True

lang.language_initialize(LANGUAGE)

# Get available output devices
mixer.init()
print("Outputs/Inputs:", devices.audio.get_audio_device_names(False))
#mixer.quit()
#mixer.init(devicename = 'MacBook Air Speakers')
#mixer.init(devicename = 'Built-in Output')
#mixer.init(devicename = "Terje’s AirPods Pro")
#mixer.init(devicename = "WH-CH510")
#mixer.init(devicename = "BS1")

#------------------------------------------------
# Point to the local server
#client = OpenAI(base_url="http://150.136.107.40:8500/v1", api_key="not-needed")
#client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

#------------------------------------------------
# Step 2: Initialize Text-to-Speech engine (Windows users only)
#engine = pyttsx3.init('dummy')
engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-40)
    
#------------------------------------------------
# Step 3: Define ANSI escape sequences for text color
colors = {
    "blue": "\033[94m",
    "bright_blue": "\033[96m",
    "orange": "\033[93m",
    "yellow": "\033[93m",
    "white": "\033[97m",
    "red": "\033[91m",
    "magenta": "\033[35m",
    "bright_magenta": "\033[95m",
    "cyan": "\033[36m",
    "bright_cyan": "\033[96m",
    "green": "\033[32m",
    "bright_green": "\033[92m",
    "reset": "\033[0m"
}

#------------------------------------------------
# Step 4: Ignore FP16 warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

#------------------------------------------------
# Step 5: Point to LM Studio Local Inference Server
#openai.api_base = "http://150.136.107.40:8500/v1"
#openai.api_base = "http://localhost:1234/v1"
#openai.api_key = "not-needed"

#------------------------------------------------
# Step 6: Load the Whisper model
whisper_model = whisper.load_model("base")  # orig=base
#whisper_model = whisper.load_model("tiny")  # orig=base

#------------------------------------------------
# Step 7: Define audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 8000  # orig = 16000
CHUNK = 1024
SHORT_NORMALIZE = (1.0/32768.0)

audio = pyaudio.PyAudio()
lastkey = '0'
lastpressed = False
my_name = "Unknown"

# MacOS
chrome_path = 'open -a /Applications/Google\ Chrome.app %s'

# Windows
# chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

# Linux
# chrome_path = '/usr/bin/google-chrome %s'

#        {'type': 'function', 'function': {'name': 'get_number', 'description': 'get_number(symbol: real) -> list - Get the next number in a sequence of numbers given by the human. Args: number (list): A list of numbers in a seemingly random order.  Returns:  real: The next number in the sequence.', \
#        'parameters': {'type': 'object', 'properties': {'symbol': {'type': 'list'}}, 'required': ['symbol']}}} \

# PS: Some how the LLM is able to create the function call shutdown even without it being in the prompt...
#        {'type': 'function', 'function': {'name': 'shutdown', 'description': 'shutdown() - The system will shut down. Args: none. Returns:  none.'}} \
#        \

# '''
#         You are provided with function signatures within <tools></tools> XML tags. \
#         You may call one or more functions to assist with the user query. \
#         Don't make assumptions about what values to plug into functions. \
#         Here are the available tools: \
#         <tools> \
#         {'type': 'function', 'function': {'name': 'shutdown', 'description': 'shutdown() - The system will shut down. Args: none. Returns:  none.'}} \
#         \
#         {'type': 'function', 'function': {'name': 'start_new', 'description': 'start_new() -> list - Start a new conversation. Args: none. Returns:  string: A new conversation.'}} \
#         \
#         {'type': 'function', 'function': {'name': 'get_number', 'description': 'get_number(symbol: real) -> list - Get the next number in a sequence of numbers given by the human. Args: number (list): A list of numbers in a seemingly random order.  Returns:  real: The next number in the sequence.', \
#         'parameters': {'type': 'object', 'properties': {'number': {'type': 'list'}}, 'required': ['number']}}} \
#         \
#         {'type': 'function', 'function': {'name': 'run_python', 'description': 'run_python(file: string) -> list - Run a python program that is stored on disk with the requested file as parameter. Args: file (string): The filename to be executed.  Returns:  string: The command result.', \
#         'parameters': {'type': 'object', 'properties': {'file': {'type': 'string'}}, 'required': ['file']}}} \
#         \
#         {'type': 'function', 'function': {'name': 'compile_arduino', 'description': 'compile_arduino(file: string) -> list - Only compile the requested arduino program. Args: file (string): The filename to be compiled.  Returns:  string: The compiler result.', \
#         'parameters': {'type': 'object', 'properties': {'file': {'type': 'string'}}, 'required': ['file']}}} \
#         \
#         {'type': 'function', 'function': {'name': 'program_arduino', 'description': 'program_arduino(file: string) -> list - Only progran the arduino board with the requested program. Args: file (string): The file name to be programmed to the board.  Returns:  string: The board programming result.', \
#         'parameters': {'type': 'object', 'properties': {'file': {'type': 'string'}}, 'required': ['file']}}} \
#         \
#         {'type': 'function', 'function': {'name': 'create_empty_git_repo', 'description': 'create_empty_git_repo(projectname: string) -> list - Create an empty GIT reposotry with the requested project name, and a default README file describing the project. Args: {projectname (string): The project name to be generated, description (string): The project description}  Returns:  string: The result.', \
#         'parameters': {'type': 'object', 'properties': {'projectname': {'type': 'string'}}, 'description': {'type': 'string'}}, 'required': ['projectname']}}} \
#         \
#         {'type': 'function', 'function': {'name': 'write_a_file', 'description': 'write_a_file(filename: string) -> list - Store a file with the given file name and content for later usage. Args: {filename (string): The filename to be generated with the reqested content, content (string): The actual file content to be stored }  Returns:  string: The result.', \
#         'parameters': {'type': 'object', 'properties': {'filename': {'type': 'string'}}, 'content': {'type': 'string'}}, 'required': ['filename','content']}}} \
#         \
#         {'type': 'function', 'function': {'name': 'get_time', 'description': 'get_time() -> list - Get the current local time. Args: none. Returns:  string: The current local time.'}} \
#         \
#         {'type': 'function', 'function': {'name': 'get_year', 'description': 'get_year() -> list - Get the current local year that we are in. Args: none. Returns:  string: The current local year.'}} \
#         \
#         {'type': 'function', 'function': {'name': 'get_date', 'description': 'get_date() -> list - Get the current local date. Args: none. Returns:  string: The current local date.'}} \
#         </tools> \
#         Use the following pydantic model json schema for each tool call you will make: \
#         {'title': 'FunctionCall', 'type': 'object', 'properties': {'arguments': {'title': 'Arguments', 'type': 'object'}, 'name': {'title': 'Name', 'type': 'string'}}, 'required': ['arguments', 'name']} \
#         For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows: \
#         <tool_call> \
#         {'arguments': <args-list>, 'name': <function-name>} \
#         </tool_call> "}
# ''' 

if LANGUAGE=="nb_NO":
    prompt = [
        {"role": "system", "content": "Ditt navn er Mary, en chatbot assistent. \
        Mitt navn er "+my_name+", en menneskelig bruker. Din rolle er å assistere menneske men navnet "+my_name+". \
        Du svarer konsisten, nøyaktig, oppretholder en vennlig tone, respektfult, og professionelt. \
        Du vektleger ærlighet, oppriktighet, og er pressis i dine svar."}
    ]
else:
    prompt = [
        {"role": "system", "content": "You are Mary, a function calling assistant chatbot. \
        My name is "+my_name+", the human and user. Your role is to assist the human. Respond concisely and accurately, maintaining a friendly, respectful, and professional tone. \
        Emphasize honesty, candor, and precision in your responses."}
    ]

conversation = prompt.copy()
#------------------------------------------------
# language  : en_US, de_DE, ...
# gender    : VoiceGenderFemale, VoiceGenderMale
def change_voice(engine, language, gender='VoiceGenderFemale'):

    voices = engine.getProperty('voices')
#    for voice in voices:
#        print("Voice: " + str(voice.name) + "   " + str(voice.languages))
        
    for voice in engine.getProperty('voices'):
        for lan in voice.languages:
            if lan.replace('-', '_') == language and gender == voice.gender:
                engine.setProperty('voice', voice.id)
                return True

    raise RuntimeError("Language '{}' for gender '{}' not found".format(language, gender))

#------------------------------------------------
# Step 8: Define function to detect key tuches
def on_press(key):
    global lastkey
    global lastpressed
    lastpressed = True
    lastkey = key

#------------------------------------------------
# Step 9: Define function to speak text
def speak(text):
    print(text)
    if not DO_NOT_SPEAK:
        engine.say(text)
        engine.runAndWait()

#------------------------------------------------
# Step 10: Define function to detect rms values
def get_rms( block ):
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...

    # we will get one short out for each 
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )

#------------------------------------------------
# Get avrage rms value for background noise...
# and time it takes to get it...
def getNoiseLevel():
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK) #, input_host_api_specific_stream_info=3)
    rms = 0.0
    start = time.time()
    for i in range(10):
        data = stream.read(CHUNK)
        x = get_rms(data)
        rms = rms + x
    rms = rms/10.0
    end = time.time()
    print("Time: " + str((end - start) / 10.0) + " seconds/fr. and rms: " + "{:.6f}".format(rms))
    stream.stop_stream()
    stream.close()
    return rms

#------------------------------------------------
# Step 11: Define function to record audio
def record_audio(rms):
    global lastkey
    global lastpressed

    frames = []
    newrms = []

    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print(f"{colors['green']}"+lang.language_get_text('start')+f"{colors['reset']}")
    lastdata = stream.read(CHUNK)
    old_x = get_rms(lastdata)

    # Wait for loud sound to start recording...
    while True:
        data = stream.read(CHUNK)
        x = get_rms(data) 
      #  print(str((x+old_x)/2.0)+" : " + str(rms*2)) #10))

        if ((x+old_x)/2.0) > (rms * 3.5):
            frames.append(lastdata) # Also add frame before the loud sound...
            frames.append(data)
            break 

        lastdata = data 
        old_x = x
        
        if lastpressed == True:
            lastpressed = False

            if str(lastkey.char) == 'q':
                return None

    # Record until sound is low enough...
    print(f"{colors['red']}"+lang.language_get_text('pause')+f"{colors['reset']}")

    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        newrms.append(get_rms(data))

        # Moving average of rms...
        if len(newrms) > 5:
            newrms.pop(0)
        x = 0
        for i in newrms:
            x = x + i
        x=x/len(newrms)

        # Check if rms is low enough to stop recording...
        if x < rms*1.5: #2:
            break 

    stream.stop_stream()
    stream.close()

#    start = time.time()
    wf = wave.open("temp_audio.wav", 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
 #   end = time.time()
 #   print("Time: " + str((end - start) / 10.0) + " seconds/fr. and rms: " + "{:.6f}".format(rms))
    return "temp_audio.wav"

#------------------------------------------------
# Step 12: Define function to get user input via GUI dialog
def get_user_input():
    ROOT = tk.Tk()
    ROOT.withdraw()  # Hide the main Tkinter window
    user_input = simpledialog.askstring(title="Text Input", prompt="Type your input:")
    return user_input

#------------------------------------------------
# Step 12: Define function to get user input via GUI dialog
def wait_for_silence():
    newrms = []

    print(f"{colors['magenta']}"+lang.language_get_text('quiet')+f"{colors['reset']}")

    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    newrms.append(get_rms(stream.read(CHUNK)))

    while True:
        newrms.append(get_rms(stream.read(CHUNK)))

        # Moving average of rms...
        if len(newrms) > 10:
            newrms.pop(0)
        x = 0
        for i in newrms:
            x = x + i
        x=x/len(newrms)

        # Check if rms is low enough to stop recording...
        if x < rms*2:
            break 

    stream.stop_stream()
    stream.close()

#------------------------------------------------
def get_number(y):
    """Get the next number in a sequence of numbers."""
    ret = 0

    for x in y:
        if type(x) == int or type(x) == float:
            ret = ret + x
        else:
            return "parameter not a number"
        
    return ret
#------------------------------------------------
def get_time():
    """Get the local time."""
    return datetime.datetime.now().strftime("%H:%M:%S")
#------------------------------------------------
def get_date():
    """Get the local date."""
    return datetime.datetime.now().strftime("%d/%m/%Y")
#------------------------------------------------
def get_year():
    """Get the local year."""
    return datetime.datetime.now().strftime("%Y")

#------------------------------------------------
def compile_arduino(file):
    print("Compiling file " + str(file) + "...")
    command = "arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32S3 "+file
    os.system(command)
    return "OK"

#------------------------------------------------
def program_arduino(file):
    print("Programming file " + file + "...")
    command = "arduino-cli upload -p /dev/tty.usbmodem11401 --fqbn esp32:esp32:XIAO_ESP32S3 "+file
    os.system(command)
    return "OK"

#------------------------------------------------
import subprocess

def run_python(file):
    print("Running file " + file + "...")
    command = "python3 " + file    
    if os.path.isfile(file):
        response = subprocess.check_output(command, shell=True, text=True)
        print(response[:100])
        return  "OK: "+response[:100]
    else:
        return "The reqested file does not exist or could not be run."
#------------------------------------------------    
def create_empty_git_repo(project, description="Empty project"):
    os.mkdir(project)
    os.chdir(project)
    command = "git init"
    os.system(command)
    command = str(project) + " > README.md"
    os.system(command)
#    os.system('git commit -a -m "Initial commit" --no-edit --dry-run ')
    os.system('git commit -a -m "Initial commit" --no-edit -q ')
    return "OK"

#------------------------------------------------
def write_a_file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)
        f.close()
    return "OK"

#------------------------------------------------
def start_new():
    global conversation
    conversation = prompt.copy()
    return "New conversation started!"

def shutdown():
    mixer.quit()
    audio.terminate()
    speak("Shutting down...")
    exit()

#------------------------------------------------
# Step 13: Define function to process user input and generate response
def process_input(input_text):
    global conversation

    conversation.append( {"role": "user", "content" : input_text})

    completion = client.chat.completions.create( model="local-model", messages=conversation, temperature=0.7 )
    assistant_reply = str(completion.choices[0].message.content)
    
    #Function calling...
    if "<tool_call...>" in assistant_reply:
        print("1-------")
        print(str(assistant_reply))
        assistant = assistant_reply #.replace("\"","$#")
        # print("2-------")
        # print(str(assistant))
        # assistant = assistant.replace("'","\"")
        # print("3-------")
        # print(str(assistant))
        # assistant = assistant.replace("$#","'")
        # pos  = 0
        # print("4-------")
        # print(str(assistant))
        print("5-------")
        
        pos = 0

        while True:
            z = assistant[pos:]
            x = z.split("<tool_call>")[1]
            x = x.split("</tool_call>")[0]
            print("---------------------------------------------------")
            print(x)
            if x[2] == '\'':
#                x = x.replace("\"","\"")
                x = x.replace("\"","#%#")
                x = x.replace("\'","\"")
                x = x.replace("#%#","\"")
                print(x)
                
            print("---------------------------------------------------")
            # print(z)
            # x = z.split("<tool_call>")[1]
            # print(x)
            # c = x.split("</tool_call>")[0]
            # print(c)
            # c = c.replace("\"","#")
            # d = c.replace("'","\"")
            # e = d.replace("#","'")
            # print(e)

            result = None
            try:
                tool_call = json.loads(x)     
                try:
                    function_name = tool_call["name"]
                except KeyError:
                    function_name = None
                    result = "This is an illegal function call"

            except json.decoder.JSONDecodeError:
                result="This is an illegal JSON formated function call, please refrace"
                function_name = None

#            tool_call = json.loads(assistant[pos:].split("<tool_call>")[1].split("</tool_call>")[0])     
            
            # Select the correct function...
            if function_name == "get_number":
                # Get the parameters...
                try:
                    number = tool_call["arguments"]["number"]
                except KeyError:
                    number = None

                if not number == None:
                    # Call the function...
                    result = get_number(number)

            if function_name == "write_a_file":
                print(tool_call["arguments"])
                project = tool_call["arguments"]["filename"]
                description = tool_call["arguments"]["content"]
                result = write_a_file(project, description)

            if function_name == "create_empty_git_repo":
                print(tool_call["arguments"])
                project = tool_call["arguments"]["projectname"]
                description = tool_call["arguments"]["description"]
                result = create_empty_git_repo(project, description)

            if function_name == "run_python":
                try:
                    file = tool_call["arguments"]["file"]
                except KeyError:
                    file = None

                if not file == None:
                    result = run_python(file)

            if function_name == "compile_arduino":
                try:
                    file = tool_call["arguments"]["file"]
                except KeyError:
                    file = None

                if not file == None:
                    result = compile_arduino(file)
                
            if function_name == "program_arduino":
                try:
                    file = tool_call["arguments"]["file"]
                except KeyError:
                    file = None

                if not file == None:
                    result = program_arduino(file)

            if function_name == "start_new":
                result = start_new()

            # Select the correct function...
            if function_name == "get_time":
                result = get_time()

            # Select the correct function...
            if function_name == "get_date":
                result = get_date()
                
            if function_name == "get_year":
                result = get_year()

            if function_name == "shutdown":
                result = shutdown()

            if result != None:
                print(result)
                # Make the assistant reply. This is always the same for all function calls...
                response = assistant[pos:assistant[pos:].find("</tool_call>") + 12]
                conversation.append( {"role": completion.choices[0].message.role, "content" : response})
                # Make the actual reply...
                answer = "<tool_response>"+str({'name': function_name,  'content' : {'answer': result}})+"</tool_response>"
                conversation.append( {"role": completion.choices[0].message.role, "content" : answer })                                
                # Run the AI again to make the full reply...
                completion = client.chat.completions.create( model="local-model", messages=conversation, temperature=0.7 )

            #------------------------------------------------
            pos=pos+assistant[pos:].find("</tool_call>") + 11
            if  not "<tool_call>" in assistant[pos:]:
           #     print(conversation)
                assistant_reply = completion.choices[0].message.content 

                conversation.append( {"role": completion.choices[0].message.role, "content" : completion.choices[0].message.content})
                speak(assistant_reply)
                break

    else:
   #     wait_for_silence()
        conversation.append( {"role": completion.choices[0].message.role, "content" : completion.choices[0].message.content})
        speak(assistant_reply)
    
#------------------------------------------------
# Get avrage rms value for background noise...
def get_text():
    audio_file = record_audio(rms)
    if audio_file == None:
        return None

    start = time.time()
    transcribe_result = whisper_model.transcribe(audio_file)
    transcribed_text = transcribe_result["text"]
    end = time.time()
    print("Wisper Time: " + str((end - start) / 10.0) + " seconds/fr. and rms: " + "{:.6f}".format(rms))

    os.remove(audio_file)  # Cleanup
    return transcribed_text

#------------------------------------------------
#------------------------------------------------
#------------------------------------------------
if __name__ == "__main__":

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    #------------------------------------------------
    # Get avrage rms value for background noise...
    if not RUN_QUIET:
        rms = getNoiseLevel()

    change_voice(engine, LANGUAGE, "VoiceGenderFemale")
    time.sleep(4)
    speak(lang.language_get_text('hello'))

    if RUN_QUIET:
        x = "Hei Mary my name is Terje"
    else:
        x = ""
        while x == "" and len(x) < 1:
            x = get_text()
            if len(x) < 1:
                speak(lang.language_get_text('name'))

    if x == None:
        speak("Thank you for now, hope to talk to you soon. Goodbye.")
        print("Exiting")

    else:
        x = x.split()
    #    print(x)
        my_name = x[len(x)-1]
        speak("Hey "+my_name+", "+lang.language_get_text('assist'))

        #------------------------------------------------
        # Step 14: Main loop to continuously monitor for user input
        num = 0
        while num < 1:
#        while True:
            if RUN_QUIET:
                transcribed = [
                    "Can you find a way to use python to add the two numbers 56 and 32 and take the square root of the result and print it?, store the program in a file and execute it using python, Mary",
                    "Mary, Can you write a python program that makes a websearch on wikipedia for Elon Musk, extract the information from the HTML code, and store this program to a file, and then execute the file using the python3 function ?",
                    "Mary, Can you write a python3 program that makes a websearch on google for Elon Musk?",
                    "Mary, Can you store the python program you just made to disk?",
                    "Mary, can you execute the file you just stored using the python3 function ?",
                    "Mary, Can you write a python program that makes a websearch on google for Elon Musk and print the result, then store this program to a file, and then execute the file using the python3 function ?",
                    "Mary, Can you write a python program that adds the two numbers 56 and 32 and take the square root of the result and print it, then store this to a file, and then execute the file using the python3 function ?",
                    "can you store the content you just showed me to a file on disk for later usage? Mary",
#                    "Mary, Yes please",
                    "Mary, Do you know the arduino programming language",
                    "Mary, Can you write a new arduino program that will blink the led on pin 13, and save it to a file?",
                    "Mary, Can you create a GIT repositry with the name Test1, the repositry will be used for a python project that will generate test numbers from 0 to 100?",
                    "Mary, Can you program the arduino board with the file Blink?",
                    "Mary, Can you compile the arduino file Blink, and then program it to the arduino board?",
                    "Hey Mary, who was the president in the United States twenty years ago?",
                    "Hey Mary, What is the difference between alcohols and carboxylic acids?",
                    "Hey Mary, in a sequence of numbers 1, 2, 5, 13 what is the next number?",
                    "Mary, Who was the president in the United States in 1990?",
                    "and who was next president in the United States after that, Mary?",
                    "Mary, if you take a sequence of numbers, 1, 1, 2, 4, 6, what would be the next number? And could you at the same time also tell me what time it is?. And what year are we inn?. And what is todays date?"]
                transcribed_text = transcribed[num]
                num=num+1
                if num == len(transcribed): num = 0
            else:
                transcribed_text = get_text()

            if transcribed_text == None or "exit this program" in transcribed_text:
                if LANGUAGE == "nb_NO":
                    speak("Takk for nå, ha en god dag.")
                else:
                    speak("Thank you for now, hope to talk to you soon. Goodbye.")
                print("Exiting")
                break

            print(f"{colors['blue']}VTM:{colors['reset']} {transcribed_text}")
            if "Mary" in transcribed_text:            

                transcribed_text_lower = transcribed_text.lower()

                if 'open youTube' in transcribed_text_lower:
                    speak("Here you go to Youtube\n")
                    webbrowser.get(chrome_path).open("http://youtube.com")

                
                # if 'wikipedia' in transcribed_text_lower:
                #     engine.say('Searching Wikipedia...')
                #     engine.runAndWait()
                #     transcribed_text_lower = transcribed_text_lower.replace("wikipedia", "")
                #     transcribed_text_lower = transcribed_text_lower.replace("mary", "")
                #     print(transcribed_text_lower)
                #     results = wikipedia.summary(transcribed_text_lower, sentences = 3)
                #     speak("According to Wikipedia")
                #     speak(results)
                #     print(results)
                
                elif 'open the news' in transcribed_text_lower:
                    speak("Here you go to VG\n")
                    webbrowser.get(chrome_path).open("http://vg.no")
            
                elif 'open google' in transcribed_text_lower:
                    speak("Here you go to Google\n")
                    webbrowser.get(chrome_path).open("http://google.com")

                elif 'joke' in transcribed_text_lower:
                    speak(pyjokes.get_joke())
                
                elif 'search the web' in transcribed_text_lower:
                    transcribed_text_lower = transcribed_text_lower.replace("search the web", "") 
                    transcribed_text_lower = transcribed_text_lower.replace("mary", "")
                    print(transcribed_text_lower) 
                    webbrowser.get(chrome_path).open("https://www.google.com/search?q="+transcribed_text_lower)

                else:
                    transcribed_text = transcribed_text.replace('mary', '')
                    transcribed_text = transcribed_text.replace('Mary', '')
                    if LANGUAGE == "nb_NO":
                        speak("Så du sier.")
                    else:
                        speak("So you're saying. ")

                    speak(transcribed_text)
                    if LANGUAGE == "nb_NO":
                        speak("er dette riktig?")
                    else:
                        speak("is that correct?")

                    if RUN_QUIET:
                        x = "yes"
                    else:
                        x =  get_text().lower()

                    print(x)
                    if 'no' in x or 'not' in x or 'wrong' in x:
                        if LANGUAGE == "nb_NO":
                            speak("beklager, forsøk igjen!")
                        else:
                            speak("sorry, please repeat the question!")
                    else:
                        if LANGUAGE == "nb_NO":
                            speak("La meg tenke et øyeblikk!")
                        else:
                            speak("Let me think for a moment")

                        process_input(transcribed_text)
        
    #------------------------------------------------
    # Step 15: Cleanup audio resources
        mixer.quit()
        audio.terminate()
