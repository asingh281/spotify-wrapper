import sys
from inspect import signature
from spotify_utils import get_spotify_client, get_active_device_id, get_current_track, get_top_tracks
from track_database import TrackDB

DB_PATH = 'track_weights.db'
MAX_WEIGHT = 1.0

def like():
    track = get_current_track(client)
    if not track:
        print('No track is currently playing.')
        return
    old = db.get_weight(track.id)
    if old is None:
        new = MAX_WEIGHT / 2
        db.add_track(track, MAX_WEIGHT / 2)
    else:
        new = old + (MAX_WEIGHT - old) / 2
        db.set_weight(track.id, new)
    print(f'Liked {track.info()}. New weight: {new:.2f}.')

def dislike():
    track = get_current_track(client)
    if not track:
        print('No track is currently playing.')
        return
    old = db.get_weight(track.id)
    if old is None:
        new = 0
        db.add_track(track)
    else:
        new = old / 2
        db.set_weight(track.id, new)
    print(f'Disliked {track.info()}. New weight: {new:.2f}.')

def track_info():
    track = get_current_track(client)
    if track:
        weight = db.get_weight(track.id)
        print(f'Currently playing: {track.info()}.', "Weight:", f"{weight:.2f}" if weight else weight)
    else:
        print('No track is currently playing.')

def list_tracks():
    tracks = db.get_tracks()
    for track, weight in tracks:
        print(f"{weight:.2f}", track.info())
    print(f'Number of tracks: {db.num_tracks()}')

def queue_tracks(n = 1):
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
        track = db.get_random_track()
        client.add_to_queue(track.id, device)
        print(f'Queued {track.info()}.')

COMMANDS = {
    ('like', 0): like,
    ('dislike', 0): dislike,
    ('info', 0): track_info,
    ('list', 0): list_tracks,
    ('queue', 0): queue_tracks,
    ('queue', 1): queue_tracks,
    ('exit', 0): sys.exit
}

COMMAND_LIST = ', '.join(
    f'{name} {' '.join(signature(function).parameters.keys())}' if num_args else name
    for (name, num_args), function in COMMANDS.items()
)

if __name__ == "__main__":
    client = get_spotify_client()
    db = TrackDB(DB_PATH)
    if db.num_tracks() == 0:
        top_tracks = get_top_tracks(client)
        if top_tracks:
            db.fill_db(*top_tracks, MAX_WEIGHT)
            print("Filled database with your top tracks.")
    print('Available commands:', COMMAND_LIST)
    while True:
        command = input('Enter command: ').strip().casefold().split()
        args = command[1:]
        command = command[0]
        if (func := COMMANDS.get((command, len(args)))):
            func(*args)
        else:
            print('Unrecognized command. Please enter one of the following:', COMMAND_LIST)