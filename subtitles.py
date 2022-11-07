import re
import sys
import os
import pathlib


DIRECTORY = str(sys.argv[1])
files = {}
videos = {}
subs = {}


def find_files():
    for subdir, dirs, files in os.walk(DIRECTORY):
        for f in files:
            if f.endswith(".mp4"):
                year = four_digits(f)
                if year is not None:
                    videos[year] = f
            if f.endswith(".srt"):
                year = four_digits(f)
                if year is not None:
                    subs[year] = f, subdir

def rename_subs():
    for key in subs:
        if key in videos:
            sub, path = subs[key]
            ext = pathlib.Path(sub).suffix
            vid = videos[key].replace(pathlib.Path(videos[key]).suffix, "")
            new_sub_name = f"{vid}.en{ext}"
            print(f"Renaming {subs[key][0]} to {new_sub_name}")
            old_name = os.path.join(path, sub)
            new_name = os.path.join(path, new_sub_name)
            os.rename(old_name, new_name)


def four_digits(s):
    # TODO fix
    m = re.search('\d{4}', s)
    if m:
        return m.group(0)
    return m

def main():
    if len(sys.argv) < 2:
        print("No Directory given in argument")
        exit()

    find_files()
    rename_subs()

    




if __name__ == "__main__":
    main()