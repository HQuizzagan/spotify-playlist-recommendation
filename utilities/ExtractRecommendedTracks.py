# Generates list of recommended tracks based solely on SEED_TRACKS. Since it's limited to only 5 seed tracks, the trick is to
# 1. Predetermine THREE songs from the FULL DATASET that you want to use as seed tracks. They shall be chosen such that they are the most representative of the playlist.
# 2. Use the latest two songs from the FULL DATASET as additional seed tracks.

import requests
import tqdm
import pandas as pd

def getRecommendationAttributes(seedTrackInfos):
    '''
    Gets the 'min' and 'max' values for the DANCEABILITY, ENERGY, and VALENCE of the seed tracks to be used for generating the recommendations:
    
    INPUT:
        trackInfos (list of dicts): List of track informations for the seed tracks as dictionaries
        
    OUTPUT:
        recommendationAttributes (dict): Dictionary containing the 'min' and 'max' values for the DANCEABILITY, ENERGY, and VALENCE from the entire list of the seed tracks.
    '''
    danceability = [track['danceability'] for track in seedTrackInfos]
    energy = [track['energy'] for track in seedTrackInfos]
    valence = [track['valence'] for track in seedTrackInfos]
    
    recommendationAttributes = {
        'danceability': {
            'min': min(danceability),
            'max': max(danceability),
        },
        'energy': {
            'min': min(energy),
            'max': max(energy),
        },
        'valence': {
            'min': min(valence),
            'max': max(valence),
        },
    }
    
    return recommendationAttributes

def generateRecommendations(access_token, seedTrackInfos, num_tracks=50):
    '''
    Generates list of 50 recommended tracks based on the provided 5 seed tracks.
    
    INPUT:
        access_token (str): The access token for this app to access Spotify's API.
        seedTrackInfos (list of dicts): List of track informations for the seed tracks as dictionaries
        
    OUTPUT:
        recommended_tracks (list): List of recommended tracks.
    '''
    
    # Aside from the seedTrackInfos, we also use the danceability, energy, and valence of the seed tracks as the basis for the recommendations.
    recommendationAttributes = getRecommendationAttributes(seedTrackInfos)
    
    base_url = f"https://api.spotify.com/v1/recommendations?limit={num_tracks}&seed_tracks={'%2C'.join([track['id'] for track in seedTrackInfos])}&min_danceability={recommendationAttributes['danceability']['min']}&max_danceability={recommendationAttributes['danceability']['max']}&min_energy={recommendationAttributes['energy']['min']}&max_energy={recommendationAttributes['energy']['max']}&min_valence={recommendationAttributes['valence']['min']}&max_valence={recommendationAttributes['valence']['max']}"
    
    # Request for the 50 recommended songs
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    
    response = requests.get(base_url, headers=headers).json()
    
    # Response is expected to container 'seeds' and 'tracks' keys which in turn are composed of lists. We only get the 'tracks' and store it as a dataframe.
    recommended_tracks = response['tracks']
    
    return recommended_tracks