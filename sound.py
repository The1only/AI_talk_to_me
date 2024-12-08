import pyttsx3
engine = pyttsx3.init()
#hazel_voice_id = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-GB_HAZEL_11.0"
#engine.setProperty('voice', hazel_voice_id)
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-50)

def speak(text):
    engine.say(text)
    engine.runAndWait()

speak("Let me think for a moment")



""" # import required libraries
import sounddevice as sd
from scipy.io.wavfile import write
#import wavio as wv

# Sampling frequency
freq = 8000

# Recording duration
duration = 10

# Start recorder with the given values 
# of duration and sample frequency
recording = sd.rec(int(duration * freq), 
				samplerate=freq, channels=1)

# Record audio for the given number of seconds
sd.wait()

# This will convert the NumPy array to an audio
# file with the given sampling frequency
write("recording0.wav", freq, recording)

# Convert the NumPy array to audio file
#wv.write("recording1.wav", recording, freq, sampwidth=1) """
