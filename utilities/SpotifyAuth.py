import requests
import os
import streamlit as st
# import toml
# Load the TOML file
# config = toml.load('config.toml')
# from dotenv import load_dotenv
# load_dotenv()


def getAppAccessToken():
    '''
    Function to request for an Access Tokn for the app from Spotify. The access tokens last for an hour so the app needs to request for a new one every hour.

    Note that this is for server-to-server authentication as described in https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow.

    This means that with this Access Token, you can only access public data from Spotify. You cannot access private data like a user's playlists.
    '''

    # We use the "Client Credentials Flow" from Spotify's Authorization Guide
    body_params = {'grant_type': 'client_credentials'}
    url = 'https://accounts.spotify.com/api/token'

    # Make a POST request to the Spotify Accounts service with the body parameters
    auth_response = requests.post(
        url,
        data=body_params,
        # auth=(os.getenv('SPOTIFY_CLIENT_ID'),
        #       os.getenv('SPOTIFY_CLIENT_SECRET'))
        # auth=(
        #     config['spotify']['SPOTIFY_CLIENT_ID'],
        #     config['spotify']['SPOTIFY_CLIENT_SECRET']
        # )
        auth=(
            st.secrets['SPOTIFY_CLIENT_ID'],
            st.secrets['SPOTIFY_CLIENT_SECRET']
        )
    ).json()

    return auth_response

def validateToken(access_token):
    '''
    Checks if the current access token is still valid by sending a simple request to Spotify's API. If it is not valid, request for a new one, and save it to the environment variables.
    
    INPUT
        access_token (str) - The current access token to be validated
        
    OUTPUT
        spotify_access_token (str) - The new access token if the current one is invalid
        response (dict) - The response from the API
        success (bool) - True if authentication is successful, False otherwise
    '''

    try:
        url = f"https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M"
        headers = {
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(url, headers=headers).json()

        # Check if response is error or not
        if 'error' in response:

            # If the response is an error, then the token is invalid. Request for a new token and replace the environment variable
            spotify_access_token = getAppAccessToken()['access_token']
                    
            # Save the new access token to the .env file
            # with open('.env', 'r') as f:
            #     lines = f.readlines()

            #     # Modify the line that contains the variable
            #     new_lines = []
            #     for line in lines:
            #         if line.startswith('SPOTIFY_ACCESS_TOKEN='):
            #             line = f'SPOTIFY_ACCESS_TOKEN={spotify_access_token}\n'
            #         new_lines.append(line)

            #     # Check if a .env file exists. If not, create one first. Otherwise, just overwrite the existing one.
            #     if os.path.exists('.env'):
            #         with open('.env', 'w') as f:
            #             f.writelines(new_lines)
            #     else:
            #         with open('.env', 'x') as f:
            #             f.writelines(new_lines)

            print(f"New Spotify Access Token:\n{spotify_access_token}")

            return spotify_access_token, response, True
        else:
            return None, response, True
    except Exception as e:
        print(f"Exception:\n{e}")
        return None, f"Exception:\n{e}", False
