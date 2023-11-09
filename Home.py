import os
import json
import pandas as pd
import streamlit as st
from utilities import SpotifyAuth, Playlists, Tracks
from tabulate import tabulate

st.set_page_config(
  page_title="HOME",
  page_icon="🏠"
)

st.header('🏠 Spotify Data Scraper')
st.write('by **HQuizzagan** -- *25th July 2023*')

# Define some session state variables
st.session_state['token_is_valid'] = None
st.session_state['playlistInfo'] = None

# CALLBACK FUNCTIONS
def resetAccessToken(access_token):
    # Check if access token is still valid. If it is invalid, the function will request for a new one
    new_spotify_access_token, validateResponse, success = SpotifyAuth.validateToken(access_token)

    # Case 1: CURRENT access token is still valid
    if new_spotify_access_token is None and success:
        st.session_state['token_is_valid'] = True
        st.session_state['spotify_access_token'] = access_token
    # Case 2: CURRENT access token is invalid and a NEW access token has been generated
    elif new_spotify_access_token is not None and success:
        st.session_state['token_is_valid'] = False
        # Reset the access token
        st.session_state['spotify_access_token'] = new_spotify_access_token
    # Case 3: CURRENT access token is invalid and a NEW access token has NOT been generated
    else:
        st.session_state['token_is_valid'] = False
        st.session_state['spotify_access_token'] = None
        st.error(f'''
                 There was an error in validating your access token.
                 Error:
                    {validateResponse}''')
        st.stop()

    return validateResponse


# MAIN LAYOUT OF THE APP
st.info('*This app allows you to request data from Spotify\'s API. You can request for a playlist, track, artist, or album. You can also request for multiple playlists, tracks, artists, or albums.*')

with st.sidebar:
    st.header('Data Request')
    st.write("*You need a **SPOTIFY ACCESS TOKEN** before we can use the Spotify Web API to request for data. Unfortunately, the access token only has a validity of one hour. Thus, you will need to request for new tokens when it's no longer valid.*")

    spotify_access_token = st.text_input(
        label='Spotify Access Token',
        key='spotify_access_token_input'
    )

    if spotify_access_token:
        # Validate the token
        if st.button('Validate Token'):
            validateResponse = resetAccessToken(spotify_access_token)

            if st.session_state.token_is_valid:
                st.success('Token is valid.')
                st.balloons()
            else:
                st.error(f"Token is invalid. Error: {validateResponse}")
                st.stop()

                st.write(
                    f"A new access token has been generated. Please copy the new access token and paste it in the text box.")
                st.text(f"{st.session_state.spotify_access_token}")

    st.write('Select which data you want to request from Spotify.')

    # Create a selectbox: Playlist, Track, Artist, Album
    data_request_type = st.selectbox(
        label='Data Request Type',
        options=('Playlist', 'Track', 'Artist', 'Album'),
        key='data_request_type_selectbox',
    )

    if data_request_type:
        input_id = st.text_input(
            label=f"{data_request_type.upper()} ID:",
            key=f"{data_request_type.lower()}_id_input"
        )

if input_id:
    playlistInfo, playlistData = Playlists.getPublicPlaylist(
        st.session_state['spotify_access_token'],
        input_id
    )

    # Save playlistInfo to session state
    st.session_state['playlistInfo'] = playlistInfo

    if 'error' not in playlistData:
        # Write information about the album to be scraped
        st.subheader(f"Playlist Information:")
        st.markdown(
            f"""
                **Name:** {playlistInfo['name']}\n
                **Created By:** {playlistInfo['owner']}\n
                **Number of Tracks:** {len(playlistData)}\n
                **Number of Followers:** {playlistInfo['followers']}\n
                **Description:** {playlistInfo['description']}
            """
        )

        # Extract the tracks in the playlist
        trackList_df = Playlists.extractTracks(playlistData)

        # Display a spinner while the data is being loaded
        while trackList_df is None:
            st.spinner()

        st.subheader(f"Track List:")
        st.dataframe(trackList_df, use_container_width=True)

        name, id = playlistInfo['name'], playlistInfo['id']

        # Create a 2-column layout each containing a button
        col1, col2 = st.columns(2)
        # Create a download button
        with col1:
            download_button = st.download_button(
                'Download Track List Data as CSV',
                key='download_button',
                data=trackList_df.to_csv(index=False).encode('utf-8'),
                file_name=f'{name.title()}-{id}.csv',
                mime='text/csv',
            )
            
        # Check if the `output` folder exists. If not, create it.
        if not os.path.exists('output'):
            os.mkdir('output')

        # Save the playlist to a JSON file
        filename = f'output/{data_request_type.lower()}/{name.title()}--{id}.json'
        with open(filename, 'w') as f:
            json.dump(playlistData, f, indent=4)

        st.success(f"Playlist data has been saved to {filename}")

        if col2.button('Extract Audio Features'):
            audioFeatures = Tracks.getAudioFeatures(
                st.session_state['spotify_access_token'],
                trackList_df['id'].values
            )
            
            # Display success once the audio features have been extracted
            while audioFeatures is None:
                st.spinner()
            st.balloons()
            st.success(f"Audio features have been extracted successfully.")
            
            # Save to the global variable
            audioFeatures_df = pd.DataFrame(audioFeatures)
            st.dataframe(audioFeatures_df)
            
            print(f"Audio Features 1:\n\n")
            print(tabulate(audioFeatures_df.head(), headers='keys', tablefmt='psql'))
            
            # Check if the `output/temporary_storage` folder exists
            if not os.path.exists('output/temporary_storage'):
                os.mkdir('output/temporary_storage')

            # Save the trackList_df and audioFeatures_df to temporary_storage folder
            if trackList_df is not None and audioFeatures_df is not None:
                trackList_df.to_csv(f"output/temporary_storage/{name}-{id}-track-list.csv", index=False)
                audioFeatures_df.to_csv(f"output/temporary_storage/{name}-{id}-audio-features.csv", index=False)
                
                st.success(f"Track list and audio features data has been saved to output/temporary_storage folder.")

    else:
        st.error(f"Error: {playlistData['error']['message']}")
