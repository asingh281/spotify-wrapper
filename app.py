import os
import sys
from inspect import signature
from spotify_utils import get_spotify_client, get_active_device_id, get_current_track, get_track_info
from track_database import init_db, like_track, dislike_track, get_tracks, choose_track, DB_PATH

def like():
    track_id = get_current_track(client)
    if not track_id:
        print('No track is currently playing.')
        return
    weight = like_track(track_id)
    print(f'Liked {get_track_info(client, track_id)}. New weight: {weight:.2f}.')

def dislike():
    track_id = get_current_track(client)
    if not track_id:
        print('No track is currently playing.')
        return
    weight = dislike_track(track_id)
    print(f'Disliked {get_track_info(client, track_id)}. New weight: {weight:.2f}.')

def track_info():
    track_id = get_current_track(client)
    if track_id:
        print(f'Currently playing: {get_track_info(client, track_id)}.')
    else:
        print('No track is currently playing.')

def list_tracks():
    tracks = get_tracks(lambda track_id: get_track_info(client, track_id))
    for track_id, weight, info in tracks:
        print(track_id, f"{weight:.2f}", info)
        # print(track_id, round(weight*100), info)

def queue_track(n = 1):
    if not isinstance(n, int):
        try:
            n = int(n)
        except TypeError:
            print('Could not parse number of tracks to queue.')
            return
    device = get_active_device_id(client)
    if not device:
        print('Could not find a device to queue tracks.')
        return
    for _ in range(n):
        track_id = choose_track()
        client.add_to_queue(track_id, device)
        print(f'Queued {get_track_info(client, track_id)}.')

COMMANDS = {
    ('like', 0): like,
    ('dislike', 0): dislike,
    ('info', 0): track_info,
    ('list', 0): list_tracks,
    ('queue', 0): queue_track,
    ('queue', 1): queue_track,
    ('exit', 0): sys.exit
}

COMMAND_LIST = ', '.join(
    f'{name} {' '.join(signature(function).parameters.keys())}' if num_args else name
    for (name, num_args), function in COMMANDS.items()
)

if __name__ == "__main__":
    client = get_spotify_client()
    if os.path.exists(DB_PATH):
        init_db()

    print('Available commands:', COMMAND_LIST)
    while True:
        command = input('Enter command: ').strip().casefold().split()
        args = command[1:]
        command = command[0]
        if (func := COMMANDS.get((command, len(args)))):
            func(*args)
        else:
            print('Unrecognized command. Please enter one of the following:', COMMAND_LIST)