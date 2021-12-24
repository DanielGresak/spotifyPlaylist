import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
# import lxml
from pathlib import Path


def get_spotify(client_id, secret):
    SPOTIPY_REDIRECT_URI = "http://example.com"
    SCOPE = 'playlist-modify-private'
    CACHE = '.spotipyoauthcache'
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(client_id, secret, SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE)
    )


def get_api_credentials():
    # USING DOTENV AND OS TO HIDE API INFORMATION
    dotenv_path = Path('.env')
    load_dotenv(dotenv_path=dotenv_path)

    return {
        "secret": os.getenv("secret"),
        "client_id": os.getenv("client_id"),
    }


def get_top_100_songs_from_specific_day(date):
    return f"https://www.billboard.com/charts/hot-100/{date}"


def get_http_request(url):
    return requests.get(url).text


def get_soup_container(markup):
    soup = BeautifulSoup(markup, "lxml")
    return soup.find_all("li", class_="o-chart-results-list__item")


def get_songs(soup_container):
    song_dict = {}
    for song in soup_container:
        title_list = song.find_all("h3", class_="c-title")
        # FINDING THE TITLE
        for t in title_list:
            if t.text != "":
                title = t.text
                title = title.strip()
                title = title.lower()
        artist_list = song.find_all("span", class_="c-label")
        count = 1
        # FINDING THE ARTIST NAME
        for a in artist_list:
            if a != "":
                artist = a.text
                artist = artist.strip()
                artist = artist.lower()

        try:
            # I FOUND THAT MY SEARCH BROUGHT BACK 2 DIGIT NUMBERS OR THE WORD NEW. SO CHECKED FOR THAT BEFORE ADDING IT AS
            # AN ARTIST
            if len(artist) >= 3 and artist != "new" and artist != "re-\nentry":
                song_dict.update({title: artist})
        # CATCHING IF ARTIST WASN'T FOUND
        except NameError:
            print("Artist not found")

    return song_dict


def get_list_of_urls(songs, sp):
    list_of_uris = []
    spotify_dict = {}
    not_found = []
    for key, value in songs.items():
        # SEARCHING FOR TRACK
        try:
            results = sp.search(f"track: {key} artist:{value}", type="track")
            items = results["tracks"]["items"]
            spotify_key = items[0]['name'].lower()
            spotify_dict[spotify_key] = items[0]['album']['artists'][0]['name'].lower()

            list_of_uris.append(items[0]['uri'])
        except IndexError:
            not_found.append((key, value))

    print(get_not_found(not_found, songs, spotify_dict ))
    return list_of_uris


def get_not_found(not_found, web, spotify):
    return f"\nWe could not find the following songs: \n \n{not_found} \n \n And the following artists may not match: \n \n{check_artists(web, spotify)}"


def check_artists(songs_from_web, songs_from_spotify):
    artists_not_matched = []

    for key, value in songs_from_web.items():

        if key in songs_from_spotify.keys():
            if songs_from_spotify[key] not in songs_from_web[key]:
                song = (f"Title: {key}", songs_from_spotify[key], songs_from_web[key])
                artists_not_matched.append(song)
    return artists_not_matched


def main():
    # ASKING FOR THE DATE WANTED
    date = input("Please choose a date in YYY-MM-DD format: ")
    
    url = get_top_100_songs_from_specific_day(date)
    http = get_http_request(url)

    soup = get_soup_container(http)

    songs = get_songs(soup)

    # Get Spotify
    creds = get_api_credentials()
    sp = get_spotify(creds["client_id"], creds["secret"])
    user_id = sp.current_user()["id"]

    # CREATES NEW PLAYLIST WITH THE DATE AS TITLE
    playlist = sp.user_playlist_create(user=user_id, name=date, public=False)

    # ADDS LIST OF SONGS TO PLAYLIST
    sp.playlist_add_items(
        playlist_id=playlist["id"],
        items=get_list_of_urls(songs, sp)
    )





main()