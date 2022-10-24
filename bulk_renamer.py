import os
import sys


# TODO make sure user cannot pop every element from new stack


DIR = ""
EXTENSIONS = ['.mp4', '.mkv', '.mov', '.avi']
files = {}


class to_change():
    def __init__(self, original, path, ext):
        self.original = original
        self.path = path
        self.new = [original]
        self.ext = ext

def replace_str(old, new):
    for elem in files.values():
        temp = elem.new[-1]
        elem.new.append(temp.replace(old, new))



def remove_from_end(n):
    for elem in files.values():
        temp = elem.new[-1]
        # removes last n characters from file except for the extension
        elem.new.append(f"{temp[:len(temp) - (n + len(elem.ext))]}{elem.ext}")


def remove_from_front(n):
    for elem in files.values():
        temp = elem.new[-1]
        # removes first n characters from file
        elem.new.append(f"{temp[n:]}")

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

    remove_from_end(8)
    remove_from_front(6)
    replace_str("-", "")
    replace_str("  ", " ")
    print(rename_files())




    
    
    # for elem in files.values():
    #     print(elem.new[-1])











if __name__ == "__main__":
    main()