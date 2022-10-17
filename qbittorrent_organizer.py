# Script that puts torrent files in the proper folders
# so movie torrents would be put in the movies folder, ect.

# Author : Nolan Winsman
# Date : 10-17-2022


import qbittorrentapi

# not used
COMPLETE_STATES = ['pausedUP', 'uploading', 'stalledUP']

# folder where media is stored
DIR = r"/mnt/mount"

# dictionary to map torrent tags to folders
PATHS = {
        "movie": f"{DIR}/movies/",
        "show": f"{DIR}/shows/",
        "anime": f"{DIR}/anime",
        "cartoon": f"{DIR}/cartoons",
        "cartoon-movie": f"{DIR}/cartoon-movies",
        "anime-movie": f"{DIR}/anime-movies"
}

# instantiate a Client using the appropriate WebUI configuration
# change information to fit your login
qbt_client = qbittorrentapi.Client(
    host='localhost',
    port=8080,
    username='admin',
    password='adminadmin'
 )

# the Client will automatically acquire/maintain a logged in state in line with any request.
# therefore, this is not necessary; however, you many want to test the provided login credentials.
try:
    qbt_client.auth_log_in()
except qbittorrentapi.LoginFailed as e:
    print(e)

# retrieve all torrents and set their download folder to the corresponding tag
for torrent in qbt_client.torrents_info():
    # print(f'{torrent.name} ({torrent.state}) ({torrent.tags})')
    # torrent tag is present
    if len(torrent.tags) > 0:
        p = f"{PATHS[torrent.tags]}/"
        print(f"Setting {torrent.name} location to {p}")
        torrent.set_location(p)
