import time
import requests
from instagrapi import Client
from pathlib import Path
from datetime import datetime
import pytz
import random

USERNAME = "" # instagram username
PASSWORD = "" # instagram password

LASTFM_API_KEY = "" # lastfm api key
LASTFM_USERNAME = "" # lastfm username
COOKIE_PATH = Path(f"{USERNAME}.json")
OUTPUT_FILE = Path("notes.txt")
CET = pytz.timezone("") # timezone e.g Europe/Berlin


def generate_cookie(username, password):
    cl = Client()
    cl.login(username, password)
    cl.dump_settings(COOKIE_PATH)

def get_latest_track(username, api_key):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "user.getrecenttracks",
        "user": username,
        "api_key": api_key,
        "format": "json",
        "limit": 1
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "recenttracks" in data and "track" in data["recenttracks"]:
        track = data["recenttracks"]["track"][0]
        artist = track["artist"]["#text"]
        song = track["name"]
        return f"{artist} - {song}"
    return None

def get_song_lyrics(artist, track):
    response = requests.get(url=f"https://lrclib.net/api/get?artist_name={artist}&track_name={track}")
    if response.status_code == 200:
        lyrics = response.json()
        return lyrics['plainLyrics'].split('\n')
    else:
        return None

def random_line(lyrics):
    randomLine = random.choice(lyrics)
    if len(randomLine) > 60:
        return randomLine[:57] + "..."
    else:
        return randomLine

def main():
    if not COOKIE_PATH.exists():
        generate_cookie(USERNAME, PASSWORD)
        print("Cookies generated")

    cl = Client()
    cl.load_settings(COOKIE_PATH)
    cl.login(USERNAME, PASSWORD)

    previous_note_text = None
    i = 1

    while True:
        artist, song = get_latest_track(LASTFM_USERNAME, LASTFM_API_KEY)
        lyrics = get_song_lyrics(artist, song)

        if lyrics:
            note_text = random_line(lyrics)
        else:
            note_text = f"{artist} - {song}"

        if note_text:
            if len(note_text) > 60:
                note_text = note_text[:57] + "..."
            if note_text != previous_note_text:
                now = datetime.now(CET).strftime("%Y-%m-%d %H:%M:%S")
                print(f"{i}: {note_text}")
                cl.create_note(note_text, 0)
                with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                    f.write(f"[{now}] {note_text}\n")
                previous_note_text = note_text
                i += 1
        time.sleep(60)

if __name__ == "__main__":
    main()
