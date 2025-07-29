"""
Main application file - Modular version
"""
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# Import all modules
from youtube import YouTubeAnalytics
from ui_components import setup_page_config, load_custom_css, display_api_key_input
from tab_controllers import (
    handle_channel_search_tab, 
    handle_analytics_dashboard_tab, 
    handle_video_analysis_tab, 
    handle_transcript_tab
)

def main():
    # Setup page configuration
    setup_page_config()
    load_custom_css()
    
    # Main header
    st.markdown('<h1 class="main-header">📊 YouTube Data Science Channel Analytics</h1>', 
                unsafe_allow_html=True)
    
    # Get API key
    api_key = display_api_key_input()
    if not api_key:
        return
    
    # Initialize YouTube Analytics
    yt_analytics = YouTubeAnalytics(api_key)
    
    # Create main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Channel Search", 
        "📊 Analytics Dashboard", 
        "🎥 Video Analysis", 
        "📝 Transcript Extractor"
    ])
    
    # Handle each tab
    with tab1:
        handle_channel_search_tab(yt_analytics)
    
    with tab2:
        handle_analytics_dashboard_tab()
    
    with tab3:
        handle_video_analysis_tab(yt_analytics)
    
    with tab4:
        handle_transcript_tab(yt_analytics)

if __name__ == "__main__":
    main()
