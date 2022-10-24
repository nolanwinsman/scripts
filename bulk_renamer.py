import os
import sys

# NOTE
# in .bashrc add
# alias bulk_renamer='sudo python3 <path to .py script> "$PWD"'

DIR = ""
EXTENSIONS = ['.mp4', '.mkv', '.mov', '.avi']
files = {}


class to_change():
    def __init__(self, original, path, ext):
        self.original = original
        self.path = path
        self.new = [original] # stack of changes
        self.ext = ext

def replace_str(old, new):
    for elem in files.values():
        temp = elem.new[-1]
        temp = temp.replace(elem.ext, "") # removes the extension so that the replace will not affect it
        temp = temp.replace(old, new) # replaces old string with new string
        temp = f"{temp}{elem.ext}" # adds back the extension
        elem.new.append(temp)


def remove_from_end(n):
    for elem in files.values():
        temp = elem.new[-1]
        # removes last n characters from string except for the extension
        elem.new.append(f"{temp[:len(temp) - (n + len(elem.ext))]}{elem.ext}")


def remove_from_front(n):
    for elem in files.values():
        temp = elem.new[-1]
        # removes first n characters from string
        elem.new.append(f"{temp[n:]}")

def print_current():
    print("-------Current Iteration of Renaming-------")
    for elem in files.values():
        print(elem.new[-1])

def undo():
    for elem in files.values():
        if len(elem.new) > 1:
            elem.new.pop()

def rename_files():
    for elem in files.values():
        print(f"Renaming {elem.original} to {elem.new[-1]}")
        old = os.path.join(elem.path, elem.original)
        new = os.path.join(elem.path, elem.new[-1])
        os.rename(old, new)
        # shutil.move(old, new)
    exit()

def cleanup():
    """Replaces double spaces with single spaces
       Removes all periods except extension period
    """
    replace_str(".", "")
    replace_str("  ", " ")


def get_option(resp):
    if "replace" in resp.lower():
        args = resp.split()
        old = args[1]
        if 3 > len(args):
            new = ""
        else:
            new = args[2]
        if new == "space":
            new = " "
        replace_str(old, new)
    elif "front" in resp.lower():
        args = resp.split()
        try:
            n = int(args[1])
        except ValueError:
            print(f"{args[1]} is not a valid integer argument")
            return
        remove_from_front(n)
    elif "end" in resp.lower():
        args = resp.split()
        try:
            n = int(args[1])
        except ValueError:
            print(f"{args[1]} is not a valid integer argument")
            return
        remove_from_end(n)
    elif "cleanup" in resp.lower():
        cleanup()
    elif "undo" in resp.lower():
        undo()
    elif "rename" in resp.lower():
        rename_files()
    elif "exit" in resp.lower():
        exit()
        return
    else:
        return




def loop():
    while True:
        print_current()
        print("\n\nInput Commands\n---------------------")
        print("replace str_old str_new\t: takes in two strings and replaces all occurences of the old string with the new string")
        print("front n\t\t\t: removes the first n chars from the file")
        print("end n\t\t\t: removes the last n chars from the file")
        print("cleanup\t\t\t: applies common fixes. Read documentation for specifics")
        print("undo\t\t\t: un does your last change")
        print("rename\t\t\t: applies all the changes to the actual files")
        print("exit\t\t\t: exits the program\n")
        get_option(input())




def main():
    if len(sys.argv) < 2:
        print("No Directory given in argument")
        exit()

    global DIR
    DIR = sys.argv[1]


    for filename in os.listdir(DIR):
        f = os.path.join(DIR, filename)
        # checking if it is a file
        for ext in EXTENSIONS:
            if f.endswith(ext):
                # print(filename)
                files[filename] = to_change(filename, DIR, ext)

    if len(files) > 0:
        print()
        loop()






if __name__ == "__main__":
    main()