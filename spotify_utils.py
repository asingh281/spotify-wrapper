import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()
CACHE_PATH: str = '.cache'
SCOPE = 'user-modify-playback-state user-read-playback-state'

def get_spotify_client() -> spotipy.Spotify:
    auth_manager = SpotifyOAuth(scope=SCOPE, cache_path=CACHE_PATH)
    return spotipy.Spotify(auth_manager=auth_manager)

def get_active_device_id(sp: spotipy.Spotify) -> str | None:
    response = sp.devices()
    if not response:
        print('No response from Spotify API for devices.')
        return None
    devices = response.get('devices', [])
    if not devices:
        print('No device found.')
        return None
    for d in devices:
        if d.get('is_active'):
            return d['id']
    return devices[0]['id']

def current_track(sp: spotipy.Spotify) -> dict | None:
    current = sp.current_user_playing_track()
    if current and current.get('item'):
        return current['item']
    else:
        return None

def play_track(sp: spotipy.Spotify, track_uri: str) -> None:
    sp.start_playback(uris=[track_uri])

def track_info(track_object: dict) -> str:
    return f'{track_object["name"]} by {", ".join(artist["name"] for artist in track_object["artists"])}'