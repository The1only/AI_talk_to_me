#------------------------------------------------
# Step 1: Import necessary libraries and modules
import warnings
import pyaudio
import wave
import whisper
import openai
from openai import OpenAI
from pynput import keyboard
import os
import pyttsx3
import tkinter as tk
from tkinter import simpledialog
import time
import struct
import math
from pygame import mixer, _sdl2 as devices

print("All libraries and modules have been imported successfully... ")      
print("Booting up the system...")

# Get available output devices
mixer.init()
print("Outputs:", devices.audio.get_audio_device_names(False))
mixer.quit()
mixer.init(devicename = 'MacBook Air Speakers')

#------------------------------------------------
# Point to the local server
#client = OpenAI(base_url="http://10.19.0.112:1234/v1", api_key="not-needed")
#client = OpenAI(base_url="http://10.19.0.66:1234/v1", api_key="not-needed")
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

#------------------------------------------------
# Step 2: Initialize Text-to-Speech engine (Windows users only)
#engine = pyttsx3.init('dummy')
engine = pyttsx3.init()
#hazel_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0"
#engine.setProperty('voice', hazel_voice_id)
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-50)

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
openai.api_base = "http://localhost:1234/v1"
openai.api_key = "not-needed"

#------------------------------------------------
# Step 6: Load the Whisper model
whisper_model = whisper.load_model("tiny")  # orig=base

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
    print(f"{colors['green']}Start speaking... (Press 'q' to stop){colors['reset']}")
    lastdata = stream.read(CHUNK)
    old_x = get_rms(lastdata)

    # Wait for loud sound to start recording...
    while True:
        data = stream.read(CHUNK)
        x = get_rms(data) 
      #  print(str((x+old_x)/2.0)+" : " + str(rms*2)) #10))

        if ((x+old_x)/2.0) > (rms*2):
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
    print(f"{colors['red']}Pause when done...{colors['reset']}")
    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        newrms.append(get_rms(data))

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
# Step 13: Define function to process user input and generate response
def process_input(input_text):
    conversation = [
        {"role": "system", "content": "You are Mary, the assistant chatbot. As youre name is Mary you will answer questions addressed to Mary only. My name is "+my_name+", the human and user. Your role is to assist the human, who is known as "+my_name+". Respond concisely and accurately, maintaining a friendly, respectful, and professional tone. Emphasize honesty, candor, and precision in your responses."},
        {"role": "user", "content": input_text}
    ]

    completion = client.chat.completions.create(
        model="local-model",
        messages=conversation,
        temperature=0.7
    )

    assistant_reply = completion.choices[0].message.content
    print(f"{colors['magenta']}KITT:{colors['reset']} {assistant_reply}")
    print("I'll speak when quiet.!")
    wait_for_silence()
    speak(assistant_reply)
    
#------------------------------------------------
# Get avrage rms value for background noise...
def get_text():
    audio_file = record_audio(rms)
    if audio_file == None:
        return None

    transcribe_result = whisper_model.transcribe(audio_file)
    transcribed_text = transcribe_result["text"]
    os.remove(audio_file)  # Cleanup
    return transcribed_text

#------------------------------------------------
#------------------------------------------------
#------------------------------------------------

listener = keyboard.Listener(on_press=on_press)
listener.start()

#------------------------------------------------
# Get avrage rms value for background noise...
rms = getNoiseLevel()

engine.say("Hello, my name is Mary, what is youre name?")
engine.runAndWait()

x = get_text()
if x == None:
    print("Thank you for now, hope to talk to you soon. Goodbye.")
    engine.say("Thank you for now, hope to talk to you soon. Goodbye.")
    engine.runAndWait()
    print("Exiting")
    
else:
    x = x.split()
    my_name = x[len(x)-1]
    
    print("Hello "+my_name+", How can I assist you today?")
    engine.say("Hello "+my_name+", How can I assist you today?")
    engine.runAndWait()

    #------------------------------------------------
    # Step 14: Main loop to continuously monitor for user input
    while True:
        
        transcribed_text = get_text()
        if transcribed_text == None or "exit this program" in transcribed_text:
            engine.say("Thank you for now, hope to talk to you soon. Goodbye.")
            engine.runAndWait()
            print("Exiting")
            break

        print(f"{colors['blue']}VTM:{colors['reset']} {transcribed_text}")
        if "Mary" in transcribed_text:            
            engine.say("So you're saying. ")
            engine.runAndWait()
            engine.say(transcribed_text)
            engine.runAndWait()
            engine.say("Let me think for a moment")
            engine.runAndWait()

            process_input(transcribed_text)
    
#------------------------------------------------
# Step 15: Cleanup audio resources
mixer.quit()
audio.terminate()
