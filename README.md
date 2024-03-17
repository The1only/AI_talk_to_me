## Getting Started

This section will guide you through preparing your local machine for running the LM-Studio-Voice-Conversation project, including installing prerequisites, setting up the Python environment, and running the project.
It is also possible to run this software using the llama_cpp.server directly from a command prompt. This is easier on systems that LM Studio does not support.

### Prerequisites

Before you begin, ensure you have the following installed:

- **Miniconda or Anaconda**: Download and install from [Anaconda's official site](https://www.anaconda.com/).
- **LM Studio**: Access and information available at [LM Studio's website](https://lmstudio.ai/).

OR, if you are running the server directly from a command prompt:

- **llama_cpp.server**: pip install llama_cpp.server

I like to use Miniconda as I always work in the command shell. 

### Setting Up Your Python Environment

Follow these steps to prepare your environment:

1. **Install conda**: Follow the Miniconda/Anaconda installation instructions for your operating system available on the Anaconda website.

2. **Create a New Conda Environment**:
   ```bash
   conda create -n myenv python=3.9.18

   Replace `myenv` with a name of your choice for the environment.

3. **Activate the Environment**:
   ```bash
   conda activate myenv
   ```

### Clone the Repository
Get the project code by cloning the Voice-Conversation repository:
```bash
git clone https://github.com/The1only/AI_talk_to_me.git
```

4. **Install Required Packages**:
   Navigate to the cloned directory and install the necessary packages:
   ```bash
   pip install -r requirements.txt
   pip install git+https://github.com/openai/whisper.git
   ```

### Running the Project

5. Before running the project you must have a LLM running on your local computer or on a remote system.

   LM Studio on a local computer:
      Start LM Studio, and download an LLM model. I use "mistral-7b-instruct-v0.2.Q4_K_S.gguf" as this works very nicely. 
      Start the LLM module from within the LM Studio...

   LM Studio on a remote system:
      Start LM Studio, and download an LLM model. I use "mistral-7b-instruct-v0.2.Q4_K_S.gguf" as this works very nicely. 
      Start the LLM module from within the LM Studio...
      Get the system IP address and enter this in the speak_only.py file.

   OR, if you are running the server directly from a command prompt:
      wget the LLM model, in my case the "mistral-7b-instruct-v0.2.Q4_K_S.gguf", and put it in the "models" folder. 
      To start enter:
      python3 -m llama_cpp.server --model models/mistral-7b-instruct-v0.2.Q4_K_S.gguf --port 1234 --host 0.0.0.0 
      or you can experiment with this when you are using GPUs:
      python3 -m llama_cpp.server --model models/mistral-7b-instruct-v0.2.Q4_K_S.gguf --n_gpu_layers 1000 --port 1234 --host 0.0.0.0 --n_ctx 4096

- **LLM Python Script (`speak_only.py`)**: Main script for the language model.

6. To run the script, execute this command in your terminal:
   ```bash
   python speak_only.py
   ```

7. Exit

   Hitt ´q´ to exit the program.

8. Running

   When the program is started, the system listens for a second for the ambient noise in the room. This is then used for speech threshold. 

   The computer is named 'Mary', and she will only answer questions that in so way contain her name. 
   You can talk to others in the room, but as soon as her name is mentioned she will reply. 
   Eg: "Who was the third American president, Mary" or "Mary, who was the first American president" or "Do you know Marry, who was the second American president?"
   these are all legal questions, but she will only answer if you say "Mary" in the question.

   'Mary' listens for pauses in the talk, as humans, so when you have asked a question and are silent, she will start processing the question. 

   If you add "exit this program" in you're spoken sentence, then the program will exit.

9. Tuning

   There are several parameters that might need tuning:

      ### Get available output devices
      mixer.init()
      print("Outputs:", devices.audio.get_audio_device_names(False))
      mixer.quit()
      mixer.init(devicename = 'MacBook Air Speakers')

      You might need to change this parameter according to the printout or comment out all these lines to get the default output device.

      ### Set the voice threshold
      print(str((x+old_x)/2.0)+" : " + str(rms*2)) 
      if ((x+old_x)/2.0) > (rms*2):

      By enabling the print line you can see how strong you're voice is compared to the background, and then set the scaling factor accordingly.
      In a quiet environment, I have found 10 to be OK, in a noisy environment I have found 2 to be OK.

      ### Set the silence threshold
      Check if rms is low enough to stop recording...
      if x < rms*2:

      You might need to adjust this calar according to your ambient noise.

## Development Environment Setup

For detailed instructions on setting up and using Visual Studio Code with this project, please see [VSCode Instructions](VSCodeSetup.md).


