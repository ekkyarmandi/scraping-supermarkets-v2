from colorama import init, Fore, Style
init()

def print_red(text):
    print(Fore.RED + str(text) + Style.RESET_ALL)
    
def print_green(text):
    print(Fore.GREEN + str(text) + Style.RESET_ALL)

def print_yellow(text):
    print(Fore.YELLOW + str(text) + Style.RESET_ALL)