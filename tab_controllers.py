"""
Individual tab controller functions - Simplified for public data
"""
import streamlit as st
import pandas as pd
from data_processor import (
    load_predefined_channels, 
    process_channel_data, 
    get_channel_summary_stats,
    process_video_data,
    get_video_summary_stats
)
from ui_components import (
    display_channel_search_results, 
    display_metrics_cards, 
    display_top_channels_table,
    display_video_metrics_cards
)
from visualizations import (
    create_channel_comparison_chart, 
    create_video_performance_chart, 
    create_correlation_heatmap,
    create_engagement_trends_chart
)

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
                    if channels:
                        st.session_state.searched_channels = channels
                        st.success(f"Found {len(channels)} channels!")
    
    with col2:
        if st.button("📊 Load Predefined DS/ML Channels"):
            with st.spinner("Loading predefined channels..."):
                channel_ids = load_predefined_channels()
                channel_data = yt_analytics.get_channel_stats(channel_ids)
                if channel_data:
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
                    st.session_state.channel_data = channel_stats
                    st.success("✅ Channel analyzed! Check Analytics Dashboard.")
        
        elif selection_type == 'multiple' and st.button("Analyze Selected Channels"):
            if selected_channels:
                with st.spinner("Analyzing selected channels..."):
                    channel_data = yt_analytics.get_channel_stats(selected_channels)
                    if channel_data:
                        st.session_state.channel_data = channel_data
                        st.success(f"✅ Analyzed {len(channel_data)} channels!")

def handle_analytics_dashboard_tab():
    """Handle Analytics Dashboard tab functionality"""
    st.header("📊 Channel Analytics Dashboard")
    
    if 'channel_data' in st.session_state and st.session_state.channel_data:
        df = process_channel_data(st.session_state.channel_data)
        stats = get_channel_summary_stats(df)
        
        is_single_channel = len(df) == 1
        
        if is_single_channel:
            channel_name = df.iloc[0]['channel_title']
            st.success(f"📊 **Single Channel Analysis:** {channel_name}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Subscribers", f"{df.iloc[0]['subscribers']:,}")
            with col2:
                st.metric("Total Videos", f"{df.iloc[0]['total_videos']:,}")
            with col3:
                st.metric("Total Views", f"{df.iloc[0]['total_views']:,}")
            with col4:
                avg_views = df.iloc[0]['avg_views_per_video']
                st.metric("Avg Views/Video", f"{avg_views:,.0f}")
        else:
            st.info(f"📊 **Multi-Channel Analysis:** {len(df)} channels")
            display_metrics_cards(stats)
        
        # Main visualization
        st.plotly_chart(create_channel_comparison_chart(df), use_container_width=True)
        
        if not is_single_channel:
            display_top_channels_table(df)
            st.subheader("🔗 Correlation Analysis")
            st.plotly_chart(create_correlation_heatmap(df), use_container_width=True)
        
        if st.button("🔄 Clear Current Analysis"):
            for key in ['channel_data', 'current_channel', 'current_videos']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
    else:
        st.info("👆 Please search for channels or load predefined channels in the Channel Search tab.")

def handle_video_analysis_tab(yt_analytics):
    """Handle Video Analysis tab functionality"""
    st.header("🎥 Video Analysis")
    
    if 'channel_data' in st.session_state and st.session_state.channel_data:
        df = pd.DataFrame(st.session_state.channel_data)
        
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
                        video_df = process_video_data(videos)
                        st.session_state.current_videos = video_df
                        
                        video_stats = get_video_summary_stats(video_df)
                        display_video_metrics_cards(video_stats)
                        
                        st.plotly_chart(
                            create_video_performance_chart(video_df, selected_channel), 
                            use_container_width=True
                        )
                        
                        st.subheader("📈 Engagement Trends Over Time")
                        st.plotly_chart(
                            create_engagement_trends_chart(video_df),
                            use_container_width=True
                        )
                        
                        st.subheader("📊 Video Performance Data")
                        display_df = video_df[['title', 'views', 'likes', 'comments', 'engagement_rate', 'published_date']].copy()
                        display_df['published_date'] = pd.to_datetime(display_df['published_date']).dt.date
                        display_df['engagement_rate'] = display_df['engagement_rate'].round(2)
                        st.dataframe(display_df, use_container_width=True)
                        
                        csv = display_df.to_csv(index=False)
                        st.download_button(
                            label="💾 Download Video Data (CSV)",
                            data=csv,
                            file_name=f"{selected_channel}_video_data.csv",
                            mime="text/csv"
                        )
    
    else:
        st.info("👆 Please analyze channels first in the Channel Search or Analytics Dashboard tab.")
