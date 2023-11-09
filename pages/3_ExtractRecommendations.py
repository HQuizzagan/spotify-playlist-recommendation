import os
import streamlit as st
from tabulate import tabulate
import pandas as pd
from utilities import ExtractRecommendedTracks as Recommend
from utilities import Tracks

st.set_page_config(
  page_title="3 - Extract Recommended Songs",
  page_icon="🎶"
)

st.header('🎶 Extract Recommended Songs')

# Description
st.info('Once FULL DATASET has been generated by combining the TRACK LIST and the AUDIO FEATURES, you can use this dataset to generate list of RECOMMENDED TRACKS from Spotify\'s API.')

selected_playlist_NAME = None
selected_playlist_ID = None
full_dataset = None
seed_tracks = None
recommended_tracks_df = None

# Get session state variables
if 'playlistInfo' not in st.session_state or st.session_state['playlistInfo'] is None:
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
  
# Read the full dataset from the "output/temporary_storage" folder
try:
  full_dataset = pd.read_csv(f"output/temporary_storage/{selected_playlist_NAME}-{selected_playlist_ID}-full-dataset.csv")
except:
  st.error(f'There is no FULL DATASET generated for {selected_playlist_NAME} yet. Please go to the **🏠 Home** or **📊 Merge Dataset** page first and generate the FULL DATASET for this playlist.')
  st.stop()

st.header('Full Dataset')
st.dataframe(full_dataset)

# Extract the recommended songs
if full_dataset is not None:
  # Render things on the sidebar
  st.sidebar.info('For Spotify\'s API to generate recommended songs, you need to provide **SEED TRACKS**. These are the songs that will be used as the basis for the recommendations. You can provide up to 5 seed tracks.')
  
  # Choose three songs from the FULL DATASET that you want to use as seed tracks
  st.sidebar.subheader('MAIN Seed Tracks')
  st.sidebar.write('Choose **three** songs from the dataset that you want to use as seed tracks. They shall be chosen such that they are the **most representative** of the main CHARACTERISTIC of the playlist.')
  
  # Gather all the track 'names' from the FULL DATASET and use them as options for the selectbox. Enable multiple selection and searching. Limit to 3 selections, and default to the first 3 tracks.
  playlist_tracks = full_dataset['name'].tolist()
  
  # Make sure to convert the track names into title case
  options = [x.title() for x in playlist_tracks]
  
  main_seed_tracks = st.sidebar.multiselect(
    label='Select three songs from the dataset',
    label_visibility='hidden',
    options=options,
    max_selections=3,
    # default=options[:3],
    key='main_seed_tracks'
  )
  
  if len(main_seed_tracks) == 3:
    st.sidebar.write('OPTIONALLY, along the way of GENERATING RECOMMENDED TRACKS, you can opt to remove one seed track from this main seed tracks, and instead use three from the latest tracks as the additional seed tracks.')
    
    st.sidebar.write('ADDITIONAL Seed Track')
    
    additional_seed_tracks = st.sidebar.multiselect(
    label='Select two songs from the dataset',
    label_visibility='hidden',
    options=options,
    default=options[-2:],
    key='additional_seed_tracks'
  )
  
  # Get the index in 'options' of the selected tracks
  if main_seed_tracks and additional_seed_tracks:
    seed_tracks = main_seed_tracks + additional_seed_tracks
    seed_tracks_idx = [ options.index(x) for x in seed_tracks]
  else:
    st.error('You have not selected or completed the list of seed tracks yet.')
    st.stop()
    
  if seed_tracks_idx is not None:
    st.write(f'You have selected these songs as your seed tracks: {seed_tracks_idx}')
    
    for track in seed_tracks:
      st.markdown(f'* {track}')
      
    # Get the track infos for the corresponding seed_tracks_idx
    seedTrackInfos = full_dataset.iloc[seed_tracks_idx].to_dict('records')
    st.dataframe(pd.DataFrame(seedTrackInfos))
    
    # Create a number input from 1 to 100 only for the number of recommended tracks to generate
    num_tracks = st.number_input(
      label='Number of Recommended Tracks to Generate',
      min_value=1,
      max_value=50,
      value=50,
      step=1,
      key='num_tracks_input'
    )
    
    # Create a button to initiate the generation of the recommended tracks
    if st.button('Generate Recommended Tracks'):

      # Generate the recommended tracks
      if seedTrackInfos:
        st.header('Recommended Tracks')
        st.info('The recommended tracks will be generated based on the seed tracks you have selected. The recommended tracks will be saved in the **output/recommended_tracks** folder.')
        
        # Generate the recommended tracks
        recommended_tracks = Recommend.generateRecommendations(
          st.session_state['spotify_access_token'],
          seedTrackInfos=seedTrackInfos,
          num_tracks=num_tracks
        )
        
        st.balloons()
        
        # View the recommended tracks as a dataframe
        recommended_tracks_df = pd.DataFrame(recommended_tracks)
        st.write(f'There are {len(recommended_tracks_df)} recommended tracks.')
        st.dataframe(recommended_tracks_df)
        
        st.info('**DOWNLOAD** then open the downloaded CSV file and **manually label** each recommended track as either **0** or **1** based on whether the recommended track indeed belongs to the playlist or not. Create a LABEL column on the file and save it.')
        
        # Download the recommended tracks as CSV
        if st.download_button(
          label='Download Recommended Tracks as CSV',
          data=recommended_tracks_df.to_csv(index=False).encode('utf-8'),
          file_name=f'{selected_playlist_NAME.title()}-recommended-tracks.csv',
          mime='text/csv',
        ):
          st.balloons()

      else:
        st.error('You have not selected or completed the list of seed tracks yet.')
        st.stop()
  else:
    st.error('You have not selected or completed the list of seed tracks yet.')