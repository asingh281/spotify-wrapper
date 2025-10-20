import os
import sys
from spotify_utils import get_spotify_client, get_active_device_id, get_current_track, get_track_info
from track_database import init_db, like_track, dislike_track, view_tracks, DB_PATH

def start_playback() -> None:
    device = get_active_device_id(client)
    if device:
        if get_current_track(client):
            return
        client.start_playback(device_id = device, context_uri='spotify:playlist:14m2DsbkucFqxzW9aD3ydT')
    else:
        print('Could not find a device to start playback.')

def like() -> None:
    track_id = get_current_track(client)
    if not track_id:
        print('No track is currently playing to like.')
        return
    weight = like_track(track_id)
    print(f'liked {get_track_info(client, track_id)} (weight={weight:.2f})')

def dislike() -> None:
    track_id = get_current_track(client)
    if not track_id:
        print('No track is currently playing to dislike.')
        return
    weight = dislike_track(track_id)
    print(f'disliked {get_track_info(client, track_id)} (weight={weight:.2f})')

if __name__ == "__main__":
    client = get_spotify_client()
    if os.path.exists(DB_PATH):
        init_db()
    if len(sys.argv) > 1 and "play" in sys.argv:
        start_playback()
    
    print('commands: like, dislike, track, view, stop')
    while True:
        command = input('enter command: ').strip().casefold()
        if command == 'like':
            like()
        elif command == 'dislike':
            dislike()
        elif command == 'track':
            track_id = get_current_track(client)
            if track_id:
                print(f'Currently playing: {get_track_info(client, track_id)}')
            else:
                print('Nothing is currently playing.')
        elif command == 'view':
            view_tracks(lambda track_id: get_track_info(client, track_id))
        elif command in ('exit', 'stop'):
            sys.exit(1)
        else:
            print('unreocgnized command')