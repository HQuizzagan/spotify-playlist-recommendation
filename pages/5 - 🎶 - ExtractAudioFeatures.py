import streamlit as st
import pandas as pd
from utilities import Tracks

st.set_page_config(
  page_title="🎶 Extract Audio Features of Recommended Tracks",
  page_icon="🎶"
)

st.header('Extract Audio Features of Recommended Tracks')
st.info('Once all the 200 RECOMMENDED TRACKS have been generated **and labelled**, you can use this page to extract the corresponding AUDIO FEATURES for each recommended track.')

st.sidebar.markdown('''
    **STEPS:**
    1. Upload the raw `latest-recommended-tracks-{}.csv` file.` which already contains the **labels** for ALL of the recommended tracks.
    2. Extract the audio features of the recommended tracks.
    3. Download the final list of recommended tracks with their corresponding audio features as a CSV file and proceed to extracting the corresponding audio features for each recommended track.'''
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
    if raw_csv_df is not None and len(raw_csv_df) < 200:
        st.error('You have not extracted 200 recommended tracks yet. Please proceed to extracting the recommended tracks first.')
        st.stop()
    elif raw_csv_df is not None and len(raw_csv_df) > 200:
        st.error('You have extracted more than 200 recommended tracks. Please upload a CSV file that contains 200 recommended tracks only.')
        st.stop()
    else:
        st.success('You have extracted 200 recommended tracks. You may now proceed to extracting the audio features of each recommended track.')
        
    # Check if all the songs have been labelled
    if raw_csv_df['LABEL'].isnull().values.any():
        st.error('There are still some tracks that have not been labelled. Please label all the tracks first before proceeding to the next step.')
        st.stop()
    else:
        st.success('All the recommended tracks have been labelled.')
        
    # Show the raw CSV file
    st.subheader('200 Recommended Tracks')
    st.dataframe(raw_csv_df)
    
    # Extract the audio features of the recommended tracks
    if st.button('Extract AUDIO Features of the 200 Recommended Tracks'):
        # Extract the audio features of the recommended tracks
        recommended_tracks_audio_features = Tracks.getAudioFeatures(
            st.session_state['spotify_access_token'],
            raw_csv_df['id'].values
        )
        
        # Display success once the audio features have been extracted
        while recommended_tracks_audio_features is None:
            st.spinner()
        st.balloons()
        st.success(f"Audio features have been extracted successfully.")
        
        # Save to the global variable
        recommended_tracks_audio_features_df = pd.DataFrame(recommended_tracks_audio_features)
        st.dataframe(recommended_tracks_audio_features_df)
        
        if recommended_tracks_audio_features_df is not None:
            # # Ask for the Playlist Name and ID
            # playlist_NAME = st.text_input(
            #     label='Enter the name of the playlist',
            #     key='playlist_name',
            # )
            
            # playlist_ID = st.text_input(
            #     label='Enter the ID of the playlist',
            #     key='playlist_id',
            # )
            
            # Download as CSV file
            if st.download_button(
                label='Download Recommended Tracks with Audio Features as CSV',
                data=recommended_tracks_audio_features_df.to_csv(index=False).encode('utf-8'),
                # file_name=f'{playlist_NAME.title()}-{playlist_ID}-recommended-tracks-with-audio-features.csv',
                file_name=f'latest-recommended-tracks-with-audio-features.csv',
                mime='text/csv',
            ):
                st.balloons()
                
                # Save to temporary_storage as well
                # recommended_tracks_audio_features_df.to_csv(f'output/temporary_storage/{playlist_NAME}-{playlist_ID}-recommended-tracks-with-audio-features.csv', index=False)
                recommended_tracks_audio_features_df.to_csv(f'output/temporary_storage/latest-recommended-tracks-with-audio-features.csv', index=False)
                
                st.success('The recommended tracks with their corresponding audio features have been saved successfully.')