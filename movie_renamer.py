# TODO make sure duplicate movie years do not display
import os
import sys
from pathlib import Path
import imdb #run 'pip install IMDbPY' if you do not have the api

# GLOBAL VARIABLES
GLOBAL_MOVIES = {}
ia = imdb.IMDb() #calls the IMDb function to get an access object through which IMDB data can be retrieved
DIRECTORY = str(sys.argv[1])
TO_DELETE = set()
ILLEGAL_CHARS = ['\\','/',':','*','?','"','<','>','|'] #list of illegal chars for Windows
EXTENSIONS = ['.mp4', '.mkv', '.mov']


# struct for movies
class movie_struct():
    def __init__(self, key, title, year, path, recurse, movie_db, failed = False):
        self.key = key
        self.title = title
        self.year = year
        self.path = path
        self.recurse = recurse
        self.absolute_path = os.path.join(path, key)
        self.failed = failed
        self.movie_db = movie_db # all the results for the database query, to reduce redundancy
        self.new_file_name = ''
        self.new_folder_name = ''
    def print(self):
        print(f'\nKEY : {self.key}\nTITLE : {self.title}\nYEAR : {self.year}')
        print("------------------------------")
    def rename(self):
        if len(self.new_file_name) > 0 and len(self.new_folder_name) > 0:
            # renaming file
            old_name = self.absolute_path
            new_name = os.path.join(self.path, self.new_file_name)
            if old_name != new_name:
                print(f'Renaming {self.key} to {self.new_file_name}')
                os.rename(old_name, new_name)
            # renaming folder
            old_name = self.path
            parent = str(Path(self.path).parent.absolute())
            new_name = os.path.join(parent, self.new_folder_name)
            if old_name != new_name:
                print(f'Renaming {self.key} to {self.new_folder_name}')
                os.rename(old_name, new_name)

def remove_illegal(s):
	for c in ILLEGAL_CHARS: #for loop that goes through illegal chars
		s = s.replace(c,'') #replaces illegal char with empty space
	return s  

def movie_not_found(file):
    print("Movie not found")
    TO_DELETE.add(file)
    GLOBAL_MOVIES[file] = movie_struct("null", "null", "null", "null", "null", failed = True, movie_db = "null")


def movie_details_kickoff(file, path):
    temp = text_after_year(file)
    fixed_movie_name = remove_periods(temp)
    movies = ia.search_movie(fixed_movie_name)
    if len(movies) <= 0:
        movie_not_found(file)
    else:
        id = movies[0].getID()
        movie = ia.get_movie(id)
        print(movie)
        if movie['kind'] == 'movie':
            print(movie['year'])
            GLOBAL_MOVIES[file] = movie_struct(key = file, title = movie, year = movie['year'], path = path, recurse = 0, movie_db = movies)
        else:
            GLOBAL_MOVIES[file] = movie_struct("null", "null", "null", "null", "null", failed = True, movie_db = movies)
            movie_details(file, path, 1)



def movie_details(file, path, r):
    movies = GLOBAL_MOVIES[file].movie_db
    if r >= len(movies):
        movie_not_found(file)
        return
    id = movies[r].getID() #stores the ID of the r result of the search (if r == 0 it's the first result and so on)
    movie = ia.get_movie(id) #gets the series
    print(movie)
    if movie['kind'] == 'movie':
        print(movie['year'])
        GLOBAL_MOVIES[file] = movie_struct(key = file, title = movie, year = movie['year'], path = path, recurse = r, movie_db = movies)
    else:
        movie_details(file = file, path = path, r = (r + 1))


def text_after_year(name):
    """If the string file has four numbers in a row representing a year,
       adds parenthesis around the four numbers.
       Batman 1989xRAREx1080   ---->   Batman
    """
    pointer = 0
    year = 0
    for c in name:
        pointer += 1
        if c.isdigit():
            year += 1
        else:
            year = 0
        if year == 4:
            pointer = pointer
            return name[:pointer]
    return name

def remove_periods(s):
    """Returns the string file with all periods removed
    """
    suffix = s[len(s)-4:]
    return s[:-4].replace(".", " ") + suffix

def capitalize_first_letter(s):
    return s[0].upper() + s[1:]

def contains_multiple(path):
    count = 0
    for subdir, dirs, files in os.walk(path):
        for file in files:
            for ext in EXTENSIONS:
                if file.endswith(ext):
                    count += 1
                if count > 1:
                    return True
    return False

def fix_movie_file():
    # loops through all files directories and subdirectories
    for subdir, dirs, files in os.walk(DIRECTORY):
        for file in files:
            # deletes .txt and .exe files with "RARBG" in the filename
            if (file.endswith(".txt") or file.endswith(".exe")):
                print(f"Deleting file {file}")
                os.remove(os.path.join(subdir, file))
                continue
            
            if (file.endswith(".nfo") or file.endswith(".idx") or file.endswith(".sub")):
                print(f"Deleting {file}")
                os.remove(os.path.join(subdir, file))
                continue
            for ext in EXTENSIONS:
                if file.endswith(ext) and not contains_multiple(subdir):
                    movie_details_kickoff(file = file, path = subdir)

def create_new_names(key):
    title = GLOBAL_MOVIES[key].title
    year = GLOBAL_MOVIES[key].year
    ext = Path(GLOBAL_MOVIES[key].absolute_path).suffix
    GLOBAL_MOVIES[key].new_file_name = remove_illegal(f'{title} ({year}){ext}')
    GLOBAL_MOVIES[key].new_folder_name = remove_illegal(str(title))

def check_redundancy(key):
    movie = GLOBAL_MOVIES[key]
    new_name = os.path.join(movie.path, movie.new_file_name)
    old_name = os.path.join(movie.path, movie.key)
    if new_name.lower() == old_name.lower():
        print('Already Renamed Properly')
        return True
    return False



def validate(key):
    create_new_names(key)
    if not GLOBAL_MOVIES[key].failed and not check_redundancy(key):
        print("Is this information correct?")
        GLOBAL_MOVIES[key].print()
        res = input()
        if res != '': # the information is correct
            movie_details(file = key, path = GLOBAL_MOVIES[key].path, r = GLOBAL_MOVIES[key].recurse + 1)
            if key in GLOBAL_MOVIES:
                validate(key)


def main():
    if len(sys.argv) < 2:
        print("No Directory given in argument")
        exit()
    
    fix_movie_file()
    for key in GLOBAL_MOVIES:
        validate(key)

    for to_delete in TO_DELETE:
        del GLOBAL_MOVIES[to_delete]

    for key in GLOBAL_MOVIES:
        new_file_name = GLOBAL_MOVIES[key].new_file_name
        new_folder_name = GLOBAL_MOVIES[key].new_folder_name
        GLOBAL_MOVIES[key].rename()



if __name__ == "__main__":
    main()