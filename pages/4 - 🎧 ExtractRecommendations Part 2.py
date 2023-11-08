import streamlit as st
import pandas as pd
from utilities import ExtractRecommendedTracks as Recommend
from utilities import Tracks

st.set_page_config(
  page_title="🎶 Extract Recommended Songs Again",
  page_icon="🎶"
)

st.header('Extract Recommended Songs AGAIN')
st.info('You use this page **AFTER** labelling the initial list of recommended songs as either 0 or 1 based on whether the recommended track indeed belongs to the playlist or not. This is a MANUAL LABELLING process. In this page, you will be able to extract another list of recommended songs based on the labelled recommended songs.')

st.sidebar.markdown('''
    **STEPS:**
    1. Upload the raw `{playlist_name}-{playlist_id}-recommended-tracks.csv` file.` which already contains the **labels** for each recommended track.
    2. From the *correctly recommended tracks*, select another list of **five seed tracks** to be used for generating the next list of recommended tracks.
    3. Generate the next list of recommended tracks.
    4. Keep re-using this page until a total of 200 recommended tracks have been generated and labelled.
    5. Download the final list of recommended tracks as a CSV file and proceed to extracting the corresponding audio features for each recommended track.'''
)

# Upload a raw CSV file containing the labelled recommended tracks
uploaded_file = st.file_uploader(
    label='Upload the raw CSV file containing the labelled recommended tracks',
    type=['csv'],
    key='raw_csv_file',
)

# Get the uploaded file
if uploaded_file is not None:
    # Read the CSV file
    raw_csv_df = pd.read_csv(uploaded_file)
    
    # Check if a column called LABEL exists
    if 'LABEL' not in raw_csv_df.columns:
        st.error('The uploaded file does not contain a column called **LABEL**. Please upload a CSV file that contains a column called LABEL.')
        st.stop()

    # Check if there's already 200 recommended tracks
    if len(raw_csv_df) >= 200:
        st.error('You have already extracted 200 recommended tracks. Please proceed to extracting the audio features for each recommended track.')
        st.stop()
    else:
        remaining_tracks = 200 - len(raw_csv_df)
        st.warning(f'You have {remaining_tracks} remaining recommended tracks to extract.')
        
    # Show the raw CSV file
    st.subheader('Raw CSV File')
    st.dataframe(raw_csv_df)

    # Select NEW 5 seed tracks from the tracks labelled as 1
    st.subheader('Seed Tracks')
    seed_tracks_df = raw_csv_df[raw_csv_df['LABEL'] == 1]
    
    seed_tracks_NAMES = st.multiselect(
        label='Select five new seed tracks',
        options=seed_tracks_df['name'].values,
        key='seed_tracks',
        max_selections=5,
    )
    
    # Extract the Spotify IDs of the selected seed tracks
    seed_tracks_IDs = seed_tracks_df[seed_tracks_df['name'].isin(seed_tracks_NAMES)]['id'].values
    st.write(f"Selected seed tracks: {seed_tracks_IDs}")
    
    if len(seed_tracks_IDs) != 5:
        st.error('Please select five seed tracks.')
        st.stop()
    elif len(seed_tracks_IDs) == 5:
        # Get the AUDIO FEATURES of the selected seed tracks
        seed_tracks_audio_features = Tracks.getAudioFeatures(
            st.session_state['spotify_access_token'],
            seed_tracks_IDs,
        )
        
        st.success('The audio features for the selected seed tracks have been extracted successfully.')
        
        st.subheader('Seed Tracks Audio Features')
        st.write(seed_tracks_audio_features)
        
        num_tracks = st.number_input(
            label='Number of Recommended Tracks to Generate',
            min_value=1,
            max_value=50,
            value=50,
            step=1,
            key='num_tracks_input'
        )
        
        # Generate the next list of recommended tracks
        recommended_tracks_df = Recommend.generateRecommendations(
            st.session_state['spotify_access_token'],
            seedTrackInfos=seed_tracks_audio_features.to_dict('records'),
            num_tracks=num_tracks,
        )
        
        st.success('The new list of recommended tracks have been generated successfully.')
        
        # Show the recommended tracks
        st.subheader('Newly Recommended Tracks')
        st.write(f'There are {len(recommended_tracks_df)} newly recommended tracks.')
        st.dataframe(recommended_tracks_df)
        
        st.write('We will combine the uploaded labelled recommended tracks and the newly recommended tracks.')
        new_recommended_tracks_df = pd.concat([raw_csv_df, pd.DataFrame(recommended_tracks_df)], ignore_index=True, axis=0)
        st.dataframe(new_recommended_tracks_df)
        
        # Create a download button and tag it with the current date and time
        download_button = st.download_button(
            label='Download Latest Recommended Tracks as CSV',
            data=new_recommended_tracks_df.to_csv(index=False).encode('utf-8'),
            file_name=f'latest-recommended-tracks-{pd.Timestamp.now().strftime("%Y-%m-%d-%H-%M-%S")}.csv',
        )
        
        st.balloons()
        st.success(' AGAIN, Open the downloaded CSV file and **manually label** each NEWLY recommended track as either **0** or **1** based on whether the recommended track indeed belongs to the playlist or not. Create a LABEL column on the file and save it. **RE-UPLOAD IT ON THIS PAGE** until all 200 recommended tracks have been labelled.')
    else:
        st.stop()