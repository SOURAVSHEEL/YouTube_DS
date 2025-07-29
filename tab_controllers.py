"""
Individual tab controller functions
"""
import streamlit as st
import pandas as pd
from data_processor import (
    load_predefined_channels, 
    process_channel_data, 
    get_channel_summary_stats,
    process_video_data  # Add this import
)
from ui_components import display_channel_search_results, display_metrics_cards, display_top_channels_table
from visualizations import create_channel_comparison_chart, create_video_performance_chart, create_correlation_heatmap

def handle_channel_search_tab(yt_analytics):
    """Handle Channel Search tab functionality"""
    st.header("🔍 Find Data Science Channels")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input("Search for channels", 
                                   placeholder="e.g., python programming, machine learning, data science")
    
    with col2:
        max_results = st.selectbox("Max Results", [10, 20, 30, 50], index=1)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Search Channels", type="primary"):
            if search_query:
                with st.spinner("Searching for channels..."):
                    channels = yt_analytics.search_channels(search_query, max_results)
                    st.session_state.searched_channels = channels
    
    with col2:
        if st.button("📊 Load Predefined DS/ML Channels"):
            with st.spinner("Loading predefined channels..."):
                channel_ids = load_predefined_channels()
                channel_data = yt_analytics.get_channel_stats(channel_ids)
                st.session_state.channel_data = channel_data
                st.success(f"Loaded {len(channel_data)} channels!")
    
    # Handle search results
    if 'searched_channels' in st.session_state:
        selected_channels, selection_type = display_channel_search_results(
            st.session_state.searched_channels
        )
        
        if selection_type == 'single':
            with st.spinner("Getting channel stats..."):
                channel_stats = yt_analytics.get_channel_stats(selected_channels)
                if channel_stats:
                    st.session_state.current_channel = channel_stats[0]
                    st.success("Channel analyzed! Check Analytics Dashboard.")
        
        elif selection_type == 'multiple' and st.button("Analyze Selected Channels"):
            with st.spinner("Analyzing selected channels..."):
                channel_data = yt_analytics.get_channel_stats(selected_channels)
                st.session_state.channel_data = channel_data
                st.success(f"Analyzed {len(channel_data)} channels!")

def handle_analytics_dashboard_tab():
    """Handle Analytics Dashboard tab functionality"""
    st.header("📊 Channel Analytics Dashboard")
    
    if 'channel_data' in st.session_state:
        df = process_channel_data(st.session_state.channel_data)
        stats = get_channel_summary_stats(df)
        
        # Display metrics
        display_metrics_cards(stats)
        
        # Interactive charts
        st.plotly_chart(create_channel_comparison_chart(df), use_container_width=True)
        
        # Top performing channels table
        display_top_channels_table(df)
        
        # Correlation analysis
        st.subheader("🔗 Correlation Analysis")
        st.plotly_chart(create_correlation_heatmap(df), use_container_width=True)
        
    else:
        st.info("👆 Please search for channels or load predefined channels in the Channel Search tab.")

def handle_video_analysis_tab(yt_analytics):
    """Handle Video Analysis tab functionality"""
    st.header("🎥 Video Analysis")
    
    if 'channel_data' in st.session_state:
        df = pd.DataFrame(st.session_state.channel_data)
        
        # Channel selection
        selected_channel = st.selectbox(
            "Select a channel to analyze videos",
            options=df['channel_title'].tolist(),
            index=0
        )
        
        if selected_channel:
            channel_info = df[df['channel_title'] == selected_channel].iloc[0]
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"**Channel:** {channel_info['channel_title']}")
                st.write(f"**Subscribers:** {channel_info['subscribers']:,}")
            
            with col2:
                num_videos = st.slider("Number of videos to analyze", 10, 100, 50)
            
            if st.button("📹 Analyze Videos"):
                with st.spinner("Fetching video data..."):
                    videos = yt_analytics.get_video_details(
                        channel_info['playlist_id'], num_videos
                    )
                    
                    if videos:
                        # Process video data with engagement metrics
                        video_df = process_video_data(videos)
                        st.session_state.current_videos = video_df
                        
                        # Video performance metrics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Videos Analyzed", len(video_df))
                        with col2:
                            st.metric("Avg Views", f"{video_df['views'].mean():,.0f}")
                        with col3:
                            st.metric("Total Views", f"{video_df['views'].sum():,}")
                        
                        # Charts
                        st.plotly_chart(
                            create_video_performance_chart(video_df, selected_channel), 
                            use_container_width=True
                        )
                        
                        # Video performance table
                        st.subheader("📊 Video Performance Data")
                        display_df = video_df[['title', 'views', 'likes', 'comments', 'engagement_rate', 'published_date']].copy()
                        display_df['published_date'] = pd.to_datetime(display_df['published_date']).dt.date
                        display_df['engagement_rate'] = display_df['engagement_rate'].round(2)
                        st.dataframe(display_df, use_container_width=True)
    
    else:
        st.info("👆 Please analyze channels first in the Analytics Dashboard tab.")

def handle_transcript_tab(yt_analytics):
    """Handle Transcript Extractor tab functionality"""
    from ui_components import display_video_transcript_interface
    
    video_id, languages = display_video_transcript_interface()
    
    if video_id and st.button("📝 Extract Transcript"):
        with st.spinner("Extracting transcript..."):
            transcript_result = yt_analytics.get_video_transcript(video_id, languages)
            
            if transcript_result['success']:
                st.success(f"✅ Transcript extracted successfully! (Language: {transcript_result['language']})")
                
                # Display options
                col1, col2 = st.columns(2)
                
                with col1:
                    show_full = st.checkbox("Show full transcript", value=True)
                
                with col2:
                    show_segments = st.checkbox("Show time segments")
                
                if show_full:
                    st.subheader("📄 Full Transcript")
                    st.text_area("Transcript Text", transcript_result['text'], height=400)
                    
                    # Download button
                    st.download_button(
                        label="💾 Download Transcript",
                        data=transcript_result['text'],
                        file_name=f"transcript_{video_id}.txt",
                        mime="text/plain"
                    )
                
                if show_segments:
                    st.subheader("⏱️ Time Segments")
                    segments_df = pd.DataFrame(transcript_result['segments'])
                    st.dataframe(segments_df, use_container_width=True)
            
            else:
                st.error(f"❌ Failed to extract transcript: {transcript_result['error']}")
    
    # Show current videos for quick transcript access
    if 'current_videos' in st.session_state:
        st.subheader("🎥 Quick Access - Current Channel Videos")
        
        video_df = st.session_state.current_videos
        
        # Check if we need to process the data
        needs_processing = 'engagement_rate' not in video_df.columns
        
        if needs_processing:
            with st.spinner("Processing video data..."):
                try:
                    from data_processor import process_video_data
                    # Convert DataFrame to list of dictionaries for processing
                    video_data = video_df.to_dict('records')
                    processed_df = process_video_data(video_data)
                    st.session_state.current_videos = processed_df
                    video_df = processed_df
                except Exception as e:
                    st.warning(f"Could not process video data: {str(e)}")
                    # Add basic engagement rate calculation
                    video_df = video_df.copy()
                    video_df['engagement_rate'] = (video_df['likes'] / video_df['views'].replace(0, 1)) * 100
        
        selected_video = st.selectbox(
            "Select a video for transcript extraction",
            options=video_df['title'].tolist()
        )
        
        if selected_video:
            video_row = video_df[video_df['title'] == selected_video].iloc[0]
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Video:** {video_row['title']}")
                st.write(f"**Views:** {video_row['views']:,}")
                
                # Safe display of engagement rate
                try:
                    engagement_rate = video_row.get('engagement_rate', 0)
                    if engagement_rate == 0 and 'likes' in video_row and 'views' in video_row:
                        engagement_rate = (video_row['likes'] / max(video_row['views'], 1)) * 100
                    st.write(f"**Engagement Rate:** {engagement_rate:.2f}%")
                except Exception:
                    st.write("**Engagement Rate:** N/A")
            
            with col2:
                if st.button("📝 Get Transcript"):
                    with st.spinner("Extracting transcript..."):
                        transcript_result = yt_analytics.get_video_transcript(
                            video_row['video_id'], languages
                        )
                        
                        if transcript_result['success']:
                            st.success("✅ Transcript extracted!")
                            st.text_area("Transcript", transcript_result['text'], height=300)
                        else:
                            st.error(f"❌ Error: {transcript_result['error']}")

