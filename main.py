import time
import requests
from instagrapi import Client
from pathlib import Path

USERNAME = ""
PASSWORD = ""

LASTFM_API_KEY = ""
LASTFM_USERNAME = ""
COOKIE_PATH = Path(f"{USERNAME}.json")

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
        # return song <- for only showing songs
        return f"{artist} - {song}"
    return None

def main():
    if not COOKIE_PATH.exists():
        generate_cookie(USERNAME, PASSWORD)
        print("Cookies generated")

    cl = Client()
    cl.load_settings(COOKIE_PATH)
    cl.login(USERNAME, PASSWORD)

    previous_note_text = None

    while True:
        note_text = get_latest_track(LASTFM_USERNAME, LASTFM_API_KEY)
        if note_text:
            if len(note_text) > 60:
                note_text = note_text[:57] + "..."
            if note_text != previous_note_text:
                print(note_text)
                cl.create_note(note_text, 0)
                previous_note_text = note_text
        time.sleep(30)

if __name__ == "__main__":
    main()
