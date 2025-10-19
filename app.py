import sys
from spotify_utils import get_spotify_client, get_active_device_id, current_track, play_track, track_info

def start() -> None:
    device = get_active_device_id(client)
    if device:
        if current_track(client):
            return
        client.start_playback(device_id = device, context_uri='spotify:playlist:14m2DsbkucFqxzW9aD3ydT')
    else:
        print('Could not find a device to start playback.')

def like() -> None:
    track = current_track(client)
    if not track:
        print('No track is currently playing to like.')
        return
    print(f'liked {track_info(track)}')

def dislike() -> None:
    track = current_track(client)
    if not track:
        print('No track is currently playing to dislike.')
        return
    print(f'disliked {track_info(track)}')

if __name__ == "__main__":
    client = get_spotify_client()
    start()
    print('spotify wrapper on.')
    print('commands: like, dislike, track, stop')
    while True:
        command = input('enter command: ').strip().casefold()
        if command == 'like':
            like()
        elif command == 'dislike':
            dislike()
        elif command == 'track':
            track = current_track(client)
            if track:
                print(f'Currently playing: {track_info(track)}')
            else:
                print('Nothing is currently playing.')
        elif command in ('exit', 'stop'):
            sys.exit(1)
        else:
            print('unreocgnized command')