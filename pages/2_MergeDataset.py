import os
import streamlit as st
from tabulate import tabulate
import pandas as pd

st.set_page_config(
  page_title="2 - Merge Dataset",
  page_icon="📊"
)

st.header('📊 Merge Playlist Dataset')

# Provide description
st.info('Use this page to merge the TRACK LIST and extracted AUDIO FEATURES for the list into one FULL DATASET.')

selected_playlist_NAME = None
selected_playlist_ID = None

# Get session state variables by checking first if they exist
if 'playlistInfo' not in st.session_state:
  # Check if there's any existing Playlist data inside the `output/playlist` directory
  if not os.listdir('output/playlist'):
    st.error('You have not pulled any playlist yet. Please go to the **🏠 Home** page first and extract a public playlist.')
    st.stop()
  else:
    # Get the latest playlist
    available_playlists = [x.split('--')[0] for x in os.listdir('output/playlist')]
    availably_playlist_IDs = [x.split('--')[1] for x in os.listdir('output/playlist')]

    # Show the available playlist data to select from
    st.subheader('**Available Playlist Data**')
    selected_playlist_NAME = st.selectbox(
      label='Select a playlist to view the data',
      options=available_playlists,
      key='playlist_data_selection',
    )
    selected_playlist_ID = availably_playlist_IDs[available_playlists.index(selected_playlist_NAME)].removesuffix(".json")
    
    st.success(f'You have selected the playlist: **{selected_playlist_NAME}** with ID: **{selected_playlist_ID}**')
else:
  selected_playlist_NAME = st.session_state['playlistInfo']['name']
  selected_playlist_ID = st.session_state['playlistInfo']['id']

if selected_playlist_NAME == None or selected_playlist_ID == None:
  st.stop()
else:
  # Check if the `temporary_storage` folder contains CSV files
  if not os.listdir('output/temporary_storage'):
    st.error('You have not extracted any data yet. Please go to the **🏠 Home** page first and extract the track list and audio features of a specific playlist.')
    st.stop()
  else:
    try:
      # Read the CSV files from the "output/temporary_storage" folder
      trackList_df = pd.read_csv(f"output/temporary_storage/{selected_playlist_NAME}-{selected_playlist_ID}-track-list.csv")
      audioFeatures_df = pd.read_csv(f"output/temporary_storage/{selected_playlist_NAME}-{selected_playlist_ID}-audio-features.csv")
    except:
      st.error(f'There are no extracted data for {selected_playlist_NAME} yet. Please go to the **🏠 Home** page first and extract the track list and audio features for this playlist using the Playlist ID.')
      st.stop()
    
    st.header(f'{selected_playlist_NAME} - Track List')
    st.dataframe(trackList_df)

    st.header(f'{selected_playlist_NAME} - Audio Features')
    st.dataframe(audioFeatures_df)

    # Combine the two dataframes
    playlist_full_dataset = trackList_df.merge(audioFeatures_df, on='id', suffixes=('_track', '_audio'))

    if playlist_full_dataset is not None:
        
        if st.download_button(
            label='Merge and Download Full Dataset',
            data=playlist_full_dataset.to_csv(index=False).encode('utf-8'),
            file_name=f'{selected_playlist_NAME.title()}-full-dataset.csv',
            mime='text/csv',
        ):
            st.balloons()
            
            # Save to temporary_storage as well
            playlist_full_dataset.to_csv(f"output/temporary_storage/{selected_playlist_NAME}-{selected_playlist_ID}-full-dataset.csv", index=False)