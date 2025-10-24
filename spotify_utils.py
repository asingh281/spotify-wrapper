import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()
CACHE_PATH: str = '.cache'
SCOPE = 'user-modify-playback-state user-read-playback-state user-top-read'

class Track:
    def __init__(self, id: str, name: str, artists: list[str]):
        self.id = id
        self.name = name
        self.artists = artists
    
    def info(self) -> str:
        return f'"{self.name}" by {', '.join(self.artists)}'

def from_track_object(track_obj: dict) -> Track:
    return Track(track_obj['id'], track_obj['name'], [artist['name'] for artist in track_obj['artists']])

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

def get_current_track(sp: spotipy.Spotify) -> Track | None:
    """returns track id of currently playing track, or None if nothing is playing"""
    current = sp.current_user_playing_track()
    if current and current.get('item'):
        return from_track_object(current['item'])
    else:
        return None
    
def get_top_tracks(sp: spotipy.Spotify) -> tuple[list[Track], list[Track]] | None:
    """
    returns user's medium-term top 50 tracks and long-term top 50 tracks
    returns None if either API call fails
    """
    resp = sp.current_user_top_tracks(limit=50, time_range='medium_term')
    if not resp:
        return None
    recent_tracks = []
    for track in resp['items']:
        t = from_track_object(track)
        recent_tracks.append(t)

    
    resp = sp.current_user_top_tracks(limit=50, time_range='long_term')
    if not resp:
        return None
    old_tracks = []
    for track in resp['items']:
        t = from_track_object(track)
        old_tracks.append(t)
    return (recent_tracks, old_tracks)