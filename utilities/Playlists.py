import requests
from tqdm import tqdm
import pandas as pd


def getPublicPlaylist(access_token, playlist_id):
    '''
    Extracts the public information about the playlist itself given its ID. This also includes the items or tracks inside the playlist itself.

    INPUT:
        access_token (str): The access token for this app to access Spotify's API.
        playlist_id (str): The ID of the playlist to be extracted.

    OUTPUT:
        response (json): The JSON response from Spotify's API.
    '''

    base_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # Get info about the playlist itself
    playlist_info_full = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}", headers=headers).json()
    print(playlist_info_full)

    # Get only name and ID of the playlist
    playlist_info = {
        'name': playlist_info_full['name'],
        'id': playlist_info_full['id'],
        'uri': playlist_info_full['uri'],
        'description': playlist_info_full['description'],
        'owner': playlist_info_full['owner']['display_name'],
        'followers': playlist_info_full['followers']['total'],
    }

    # Get the playlist data = data about the tracks inside the playlist
    playlist_data = []
    while base_url:
        response = requests.get(base_url, headers=headers).json()
        playlist_data.extend(response['items'])
        base_url = response['next']

    return playlist_info, playlist_data


def extractTracks(playlist_data):
    '''
    Given a JSON data about playlist, this will extract the tracks included in the playlist.

    INPUT:
        playlist_data (np.array): List of tracks included in the playlis.

    OUTPUT:
        tracks_df (pd.DataFrame): A pandas DataFrame containing the tracks included in the playlist and their corresponding information.
    '''

    # Details to extract about each track
    trackDetails = ['id', 'name', 'disc_number', 'track_number',
                    'duration_ms', 'popularity', 'uri', 'href']

    # The tracks in the playlist
    playlistTracks = []

    for item in tqdm(playlist_data):
        trackRawData = item['track']

        trackInformation = {}

        # Extract album name
        trackInformation['Album'] = trackRawData['album']['name']

        # Extract the artists
        trackInformation['Artists'] = [artist['name']
                                       for artist in trackRawData['artists']]

        # Extract the other details about the track itself
        for detail in trackDetails:
            trackInformation[detail] = trackRawData[detail]

        playlistTracks.append(trackInformation)

    tracks_df = pd.DataFrame(playlistTracks)

    return tracks_df
