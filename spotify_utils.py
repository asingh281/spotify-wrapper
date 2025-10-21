import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()
CACHE_PATH: str = '.cache'
SCOPE = 'user-modify-playback-state user-read-playback-state'

def get_spotify_client() -> spotipy.Spotify:
    """
    returns an authenticated Spotify client
    needs SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URL as environment variables
    """
    auth_manager = SpotifyOAuth(scope=SCOPE, cache_path=CACHE_PATH)
    return spotipy.Spotify(auth_manager=auth_manager)

def get_active_device_id(sp: spotipy.Spotify) -> str | None:
    """returns the device id of the active device, or the first available device, or None if no devices are found"""
    response = sp.devices()
    if not response:
        return None
    devices = response.get('devices', [])
    if not devices:
        return None
    for d in devices:
        if d.get('is_active'):
            return d['id']
    return devices[0]['id']

def get_current_track(sp: spotipy.Spotify) -> str | None:
    """returns track id of currently playing track, or None if nothing is playing"""
    current = sp.current_user_playing_track()
    if current and current.get('item'):
        return current['item']['id']
    else:
        return None

def get_track_info(sp: spotipy.Spotify, track_id: str) -> str:
    try:
        track = sp.track(track_id)
        if not track:
            return '(track not found)'
        name = track['name']
        artists = ', '.join(artist['name'] for artist in track['artists'])
        return f'"{name}" by {artists}'
    except Exception as e:
        return f'(error fetching info: {e})'