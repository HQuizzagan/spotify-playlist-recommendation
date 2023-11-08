import requests
from tqdm import tqdm
import pandas as pd


def getAudioFeatures(access_token, track_ids_list):
    '''
    Extract audio features given a list of track IDs:

    INPUT:
        access_token (str): The access token for this app to access Spotify's API.
        track_ids (np.array): A list of track IDs.

    OUTPUT:
        audio_features (pd.DataFrame): A pandas DataFrame containing the audio features of the tracks.
    '''

    # Request per 100 tracks as per Spotify's API limit.
    track_ids = track_ids_list.copy()
    remaining_tracks = len(track_ids)

    audio_features = []
    while remaining_tracks > 0:
        if remaining_tracks >= 100:
            base_url = f"https://api.spotify.com/v1/audio-features?ids={','.join(track_ids[:100])}"
            track_ids = track_ids[100:]
            remaining_tracks -= 100
        else:
            base_url = f"https://api.spotify.com/v1/audio-features?ids={','.join(track_ids)}"
            track_ids = []
            remaining_tracks = 0

        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(base_url, headers=headers).json()
        audio_features.extend(response['audio_features'])

    return pd.DataFrame(audio_features)
