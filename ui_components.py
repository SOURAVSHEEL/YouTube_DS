"""
Streamlit UI components and layouts
"""
import streamlit as st
import pandas as pd

def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="YouTube Data Science Channel Analytics",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def load_custom_css():
    """Load custom CSS styles"""
    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            color: #FF0000;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #FF0000;
        }
        .channel-card {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

def display_api_key_input():
    """Display API key input in sidebar"""
    st.sidebar.title("🔧 Configuration")
    api_key = st.sidebar.text_input("YouTube API Key", type="password", 
                                   help="Enter your YouTube Data API v3 key")
    
    if not api_key:
        st.warning("⚠️ Please enter your YouTube API key in the sidebar to continue.")
        st.info("""
        **To get a YouTube API key:**
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Create a new project or select existing one
        3. Enable YouTube Data API v3
        4. Create credentials (API Key)
        5. Paste the key in the sidebar
        """)
        return None
    
    return api_key

def display_channel_search_results(channels):
    """Display channel search results with selection options"""
    if not channels:
        return []
    
    st.subheader("Search Results")
    selected_channels = []
    
    for i, channel in enumerate(channels):
        col1, col2, col3, col4 = st.columns([1, 3, 4, 2])
        
        with col1:
            if st.checkbox("Select", key=f"check_{i}"):
                selected_channels.append(channel['channel_id'])
        
        with col2:
            st.image(channel['thumbnail'], width=60)
        
        with col3:
            st.write(f"**{channel['title']}**")
            st.write(f"{channel['description']}")
        
        with col4:
            if st.button("Analyze", key=f"analyze_{i}"):
                return [channel['channel_id']], 'single'
    
    return selected_channels, 'multiple' if selected_channels else 'none'

def display_metrics_cards(stats):
    """Display key metrics in card layout"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Channels", stats['total_channels'])
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Subscribers", f"{stats['total_subscribers']:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Videos", f"{stats['total_videos']:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Views", f"{stats['total_views']:,}")
        st.markdown('</div>', unsafe_allow_html=True)

def display_top_channels_table(df):
    """Display top performing channels table"""
    st.subheader("📈 Top Performing Channels")
    top_channels = df.nlargest(10, 'subscribers')[
        ['channel_title', 'subscribers', 'total_videos', 'total_views']
    ]
    st.dataframe(top_channels, use_container_width=True)

def display_video_transcript_interface():
    """Display video transcript extraction interface"""
    st.header("📝 Video Transcript Extractor")
    
    # Video URL/ID input
    video_input = st.text_input(
        "Enter YouTube Video URL or Video ID",
        placeholder="https://www.youtube.com/watch?v=VIDEO_ID or just VIDEO_ID"
    )
    
    # Extract video ID from URL if needed
    video_id = None
    if video_input:
        if 'youtube.com/watch?v=' in video_input:
            video_id = video_input.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in video_input:
            video_id = video_input.split('youtu.be/')[1].split('?')[0]
        else:
            video_id = video_input
    
    # Language preferences
    languages = st.multiselect(
        "Preferred Languages (in order of preference)",
        ['en', 'hi', 'es', 'fr', 'de', 'ja', 'ko'],
        default=['en', 'hi']
    )
    
    return video_id, languages
