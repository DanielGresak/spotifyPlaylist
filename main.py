import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
# import lxml
from pathlib import Path
# USING DOTENV AND OS TO HIDE API INFORMATION
dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
client_id = os.getenv("client_id")
secret = os.getenv("secret")

SPOTIPY_REDIRECT_URI = "http://example.com"
SCOPE = 'playlist-modify-private'
CACHE = '.spotipyoauthcache'

# ASKING FOR THE DATE WANTED
date = input("Please choose a date in YYY-MM-DD format: ")

# FINDING TOP 100 SONGS FROM SPECIFIC DAY
URL = f"https://www.billboard.com/charts/hot-100/{date}"

page = requests.get(f"{URL}").text

soup = BeautifulSoup(page, "lxml")

song_container = soup.find_all("li", class_="o-chart-results-list__item")
song_dict = {}

for song in song_container:
    title_list = song.find_all("h3", class_="c-title")
    # FINDING THE TITLE
    for t in title_list:
        if t.text != "":
            title = t.text
            title = title.strip()
    artist_list = song.find_all("span", class_="c-label")
    count = 1
    # FINDING THE ARTIST NAME
    for a in artist_list:
        if a != "":
            artist = a.text
            artist = artist.strip()

    try:
        if len(artist) >= 3 and artist != "NEW":
            song_dict.update({title: artist})
    # CATCHING IF ARTIST WASN'T FOUND
    except NameError:
        print("Artist not found")

access_token = ""
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(client_id, secret, SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE)
)

user_id = sp.current_user()["id"]
list_of_uris = []
for key, value in song_dict.items():
    # SEARCHING FOR TRACK
    results = sp.search(f"track: {key}", type="track")
    items = results["tracks"]["items"]

    try:
        print(f"{key}, {value}, {items[0]['uri']}")
        list_of_uris.append(items[0]['uri'])
    except IndexError:
        print("Uri not found")

# CREATES NEW PLAYLIST WITH THE DATE AS TITLE
playlist = sp.user_playlist_create(user=user_id, name=date, public=False)

# ADDS LIST OF SONGS TO PLAYLIST
sp.playlist_add_items(playlist_id=playlist["id"], items=list_of_uris)