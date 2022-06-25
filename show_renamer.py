import os
import sys
from pathlib import Path
import imdb #run 'pip install IMDbPY' if you do not have the api
import re # regex


# GLOBAL VARIABLES
GLOBAL_SHOWS = {}
ia = imdb.IMDb() #calls the IMDb function to get an access object through which IMDB data can be retrieved
DIRECTORY = str(sys.argv[1])
TO_DELETE = []
ILLEGAL_CHARS = ['\\','/',':','*','?','"','<','>','|'] #list of illegal chars for Windows
EXTENSIONS = ['.mp4', '.mkv', '.mov', '.avi']
MAIN_SHOW_FOLDER = set()


# struct for television shows
class show_struct():
    def __init__(self, key, title, year, path, seasons, recurse, num_seasons, movie_db, failed = False):
        self.key = key
        self.title = title
        self.year = year
        self.path = path
        self.seasons = seasons # list of season_struct()
        self.recurse = recurse
        self.absolute_path = os.path.join(DIRECTORY, path)
        self.new_absolute_path = os.path.join(DIRECTORY, title)
        self.num_seasons = num_seasons # numberOfSeasons = series['number of seasons'] #stores the number of seasons the series has
        self.failed = failed
        self.movie_db = movie_db # all the results for the database query, to reduce redundancy
        self.new_file_name = ''
        self.new_folder_name = ''
    def print(self):
        episode_sum = 0
        for s in self.seasons:
            episode_sum += len(self.seasons[s].episodes)
            for e in self.seasons[s].episodes:
                print(f'S{s}E{e} {self.seasons[s].episodes[e].found}')
        print(f'\nKEY : {self.key}\nTITLE : {self.title}\nYEAR : {self.year} S: {len(self.seasons)} Total Episodes : {episode_sum}')
        print("------------------------------")

class season_struct():
    def __init__(self, season_number):
        self.season_number = season_number
        self.absolute_path = None
        self.new_absolute_path = None
        self.episodes = {} # list of episode_struct()

class episode_struct():
    def __init__(self, title, season_num, episode_num):
        self.episode_title = title
        self.filename = None
        self.path = None
        self.absolute_path = None
        self.season_num = season_num
        self.episode_num = episode_num 
        self.new_file_name = None
        self.absolute_path = None
        self.found = False

def show_not_found(path):
    print(f"Show not found for \n{path}\n\nType show name (with year) to search the proper name\nLeave input Blank to skip\n")
    i = input()
    if i == "":
        GLOBAL_SHOWS[path] = show_struct("null", "null", "null", "null", "null", "null", "null", failed = True, movie_db = None)
    else:
        show_details_kickoff(i, path)

def get_seasons_and_episodes(series):
    seasons = {}
    ia.update(series, 'episodes')
    num_seasons = series['number of seasons']
    for s in range(1, num_seasons + 1):
        num_episodes = len(series['episodes'][s])
        seasons[s] = season_struct(num_seasons)
        for e in range(1, num_episodes + 1):
            e_name = series['episodes'][s][e]
            seasons[s].episodes[e] = episode_struct(e_name, s, e)
    return seasons



def show_details_kickoff(name, path):
    shows = ia.search_movie(name)
    if len(shows) <= 0:
        show_not_found(path)
    else:
        id = shows[0].getID()
        series = ia.get_movie(id)
        print(series['kind'])
        if series['kind'] == 'tv series' or series['kind'] == 'tv mini series':
            year = series['year']
            print(f'Is the series {series} ({year})')
            seasons = get_seasons_and_episodes(series)
            GLOBAL_SHOWS[path] = show_struct(key = name, title = str(series), year = year, path = path, seasons = seasons, recurse = 0, num_seasons = series['number of seasons'], 
            movie_db = series)
        else:
            GLOBAL_SHOWS[path] = show_struct("null", "null", "null", "null", "null", "null", "null", failed = True, movie_db = shows)
            show_details(name, path, 1)

def show_details(name, path, r):
    shows = GLOBAL_SHOWS[path].movie_db
    if r >= len(shows):
        show_not_found(path)
    else:
        id = shows[r].getID()
        series = ia.get_movie(id)
        print(series['kind'])
        if series['kind'] == 'tv series' or series['kind'] == 'tv mini series':
            year = series['year']
            print(f'Is the series {series} ({year})')
            seasons = get_seasons_and_episodes(series)
            GLOBAL_SHOWS[path] = show_struct(key = name, title = str(series), year = year, path = path, seasons = seasons, recurse = 0, num_seasons = series['number of seasons'], 
            movie_db = series)

        else:
            show_details(name, path, r + 1)

def get_episode_number(filename):
    match = re.search(
        r'''(?ix)                 # Ignore case (i), and use verbose regex (x)
        (?:                       # non-grouping pattern
          e|x|episode|E|^           # e or x or episode or start of a line
          )                       # end non-grouping pattern 
        \s*                       # 0-or-more whitespaces
        ([0-9]+)                  # exactly 2 digits
        ''', filename)
    if match:
        return match.group(1)

def get_seasons_number(filename):
    match = re.search(
        r'''(?ix)                 # Ignore case (i), and use verbose regex (x)
        (?:                       # non-grouping pattern
          s|season|^              # e or x or episode or start of a line
          )                       # end non-grouping pattern 
        \s*                       # 0-or-more whitespaces
        ([0-9]+)                  # exactly 2 digits
        ''', filename)
    if match:
        return match.group(1)


def remove_illegal(s):
	for c in ILLEGAL_CHARS: #for loop that goes through illegal chars
		s = s.replace(c,'') #replaces illegal char with empty space
	return s  

def add_zeros(n):
    n = str(n)
    while len(n) <= 2:
        n = "0" + n
    return n

# def validate(key):


def fix_show_files():
    # loops through all files directories and subdirectories
    for d in os.listdir(DIRECTORY):
        already_done = False
        for subdir, _, files in os.walk(d):
            parent = str(Path(subdir).parent.absolute())
            if os.path.isfile(os.path.join(subdir, "changelog.txt")) or os.path.isfile(os.path.join(parent, "changelog.txt")):
                print(f"Script has already changed directory {d}, skipping directory")
                GLOBAL_SHOWS[d] = show_struct("null", "null", "null", "null", "null", "null", "null", failed = True, movie_db = None)
                already_done = True
                break
        if not already_done:
            print(f'\n\n-----{d}-----\n\n')
            MAIN_SHOW_FOLDER.add(d)
            show_details_kickoff(name = os.path.basename(d), path = d)
            if GLOBAL_SHOWS[d].failed == True:
                continue
            for file in files:

                if (file.endswith(".txt") or file.endswith(".exe") or file.endswith(".jpg")):
                    print(f"Deleting file {file}")
                    os.remove(os.path.join(subdir, file))
                    continue
                
                if (file.endswith(".nfo") or file.endswith(".idx") or file.endswith(".sub")):
                    print(f"Deleting {file}")
                    os.remove(os.path.join(subdir, file))
                    continue


                for ext in EXTENSIONS:
                    if file.endswith(ext):
                        if "sample" in file.lower():
                            os.remove(os.path.join(subdir, file))
                        # potentiall make sure it's a video file
                        print(file)
                        e_num = int(get_episode_number(file).lstrip('0'))
                        s_num = int(get_seasons_number(file).lstrip('0'))
                        # result = re.findall("\d[s]{0,99}[e]{0,99}", file) # finds groups of 1, 2, or 3 connected digits followed by any one of 'F', 'f', 'C', or 'c'
                        file_extension = Path(file).suffix
                        title = GLOBAL_SHOWS[d].title
                        episode_title = GLOBAL_SHOWS[d].seasons[s_num].episodes[e_num].episode_title
                        new_file_name = remove_illegal(f'{title} S0{s_num}E{add_zeros(e_num)} {episode_title}{file_extension}')

                        GLOBAL_SHOWS[d].seasons[s_num].absolute_path = os.path.join(DIRECTORY, subdir)
                        GLOBAL_SHOWS[d].seasons[s_num].episodes[e_num].path = subdir
                        GLOBAL_SHOWS[d].seasons[s_num].episodes[e_num].absolute_path = os.path.join(subdir, file)
                        GLOBAL_SHOWS[d].seasons[s_num].episodes[e_num].filename = os.path.join(subdir, file)
                        GLOBAL_SHOWS[d].seasons[s_num].episodes[e_num].found = True
                        GLOBAL_SHOWS[d].seasons[s_num].episodes[e_num].new_file_name = new_file_name




def main():
    if len(sys.argv) < 2:
        print("No Directory given in argument")
        exit()

    # for key in GLOBAL_SHOWS:
    #     # show = GLOBAL_SHOWS[key]
    #     validate(key)
    
    fix_show_files()
    for key in GLOBAL_SHOWS:
        show = GLOBAL_SHOWS[key]
        changelog = ""
        if show.failed == False:
            show.print()
            if not os.path.exists(show.new_absolute_path):
                os.mkdir(show.new_absolute_path)
            for s in show.seasons:
                season = show.seasons[s]
                season_folder = os.path.join(show.new_absolute_path, f'Season {s}')
                season.new_absolute_path = season_folder
                if not os.path.exists(season_folder):
                    os.mkdir(season_folder)
                    print(f'Creating Folder {season_folder}\n in {show.new_absolute_path}\n')
                for e in show.seasons[s].episodes:
                    episode = season.episodes[e]
                    if episode.found:
                        new_e_path = os.path.join(season_folder, episode.new_file_name)
                        print(f'\nRenaming and Moving: \n{episode.absolute_path}\n{new_e_path}\n')
                        os.rename(episode.absolute_path, new_e_path)
                if season_folder != season.absolute_path:
                    TO_DELETE.append(season.absolute_path)
                    changelog += f"Deleting {season.absolute_path}\n"
            if show.absolute_path != show.new_absolute_path:
                TO_DELETE.append(show.absolute_path)
                changelog += f"Deleting {show.absolute_path}\n"
            changelog_path = os.path.join(show.new_absolute_path, "changelog.txt")
            with open(changelog_path, 'w') as f: 
                f.write(changelog)
                f.close() 

    for filename in TO_DELETE:
        if filename is None:
            continue
        print(f'Deleting {filename}')
        try:
            if os.path.isdir(filename):
                os.rmdir(filename)
            else:
                os.remove(filename)
        except FileNotFoundError:
            print("File not found, should be fine")

if __name__ == "__main__":
    main()