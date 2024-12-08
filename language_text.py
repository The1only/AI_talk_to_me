#
text_lines = {
    "welcome": 0,
    "boot": 1,
    "start":2,
    "pause":3,
    "quiet":4,
    "hello":5,
    "name":6,
    "assist":7
}

lines=[]

def language_initialize(language):
    global lines
    with open(language+".txt") as f:
        lines = f.read().splitlines()

def language_get_text(token):        
    return lines[text_lines[token]]


#------------------------------------------------
#------------------------------------------------
if __name__ == "__main__":
    # Step 3,
    # "quiet":4: Define ANSI escape sequences for text color
    colors = {
        "orange": "\033[93m",
        "yellow": "\033[93m",
        "white": "\033[97m",
        "red": "\033[91m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "green": "\033[32m",
        "reset": "\033[0m"
    }

    my_name = "Tom"

    language_initialize("en_US")
    print(language_get_text('welcome'))
    print(language_get_text('boot'))
    print(f"{colors['green']}"+language_get_text('start')+f"{colors['reset']}")
    print(f"{colors['red']}"+language_get_text('pause')+f"{colors['reset']}")
    print(f"{colors['magenta']}"+language_get_text('quiet')+f"{colors['reset']}")
    print(language_get_text('hello'))
    print("Hey "+my_name+", "+language_get_text('assist'))

    