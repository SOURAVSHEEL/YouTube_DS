"""
Data processing and analysis functions - Public Data Only
"""
import pandas as pd
import numpy as np

def load_predefined_channels():
    """Load predefined channel IDs for data science/ML channels"""
    return [
        'UCNU_lfiiWBdtULKOw6X0Dig',  # Krish Naik
        'UCh3RpsDV8pS_fXJ6NBX4fhQ',  # Data Professor
        'UCeVMnSShP_Iviwkknt83cww',  # CodeWithHarry
        'UCYO_jab_esuFRV4b17AJtAw',  # 3Blue1Brown
        'UCtYLUTtgS3k1Fg4y5tAhLbw',  # StatQuest
        'UCfzlCWGWYyIQ0aLC5w48gBQ',  # sentdex
        'UCxX9wt5FWQUAAz4UrysqK9A',  # CS Dojo
        'UCCezIgC97PvUuR4_gbFUs5g',  # Corey Schafer
        'UCbfYPyITQ-7l4upoX8nvctg',  # Two Minute Papers
        'UCsvqVGtbbyHaMoevxPAq9Fg',  # Simplilearn
        'UCkw4JCwteGrDHIsyIIKo4tQ',  # edureka!
        'UCV0qA-eDDICsRR9rPcnG7tw',  # Joma Tech
        'UCWN3xxRkmTPmbKwht9FuE5A',  # Siraj Raval
        'UCiT9RITQ9PW6BhXK0y2jaeg',  # Ken Jee
        'UCV8e2g4IWQqK71bbzGDEI4Q'   # Tech With Tim
    ]

def process_channel_data(channel_data):
    """Process raw channel data into DataFrame with additional metrics"""
    df = pd.DataFrame(channel_data)
    
    # Add calculated fields
    df['created_year'] = pd.to_datetime(df['created_date']).dt.year
    df['avg_views_per_video'] = df['total_views'] / df['total_videos'].replace(0, 1)
    df['subscriber_to_video_ratio'] = df['subscribers'] / df['total_videos'].replace(0, 1)
    
    return df

def process_video_data(video_data):
    """Process video data and add engagement metrics"""
    if not video_data:
        return pd.DataFrame()
    
    df = pd.DataFrame(video_data)
    
    # Ensure numeric columns
    numeric_cols = ['views', 'likes', 'comments']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calculate engagement metrics
    df['engagement_rate'] = (df['likes'] / df['views'].replace(0, 1)) * 100
    df['comment_rate'] = (df['comments'] / df['views'].replace(0, 1)) * 100
    
    # Process dates
    df['published_date'] = pd.to_datetime(df['published_date'])
    
    # Calculate days since published (simplified timezone handling)
    try:
        now = pd.Timestamp.now().tz_localize(None)
        if df['published_date'].dt.tz is not None:
            published_naive = df['published_date'].dt.tz_localize(None)
        else:
            published_naive = df['published_date']
        df['days_since_published'] = (now - published_naive).dt.days
    except Exception:
        df['days_since_published'] = 0
    
    return df

def get_channel_summary_stats(df):
    """Generate summary statistics for channels"""
    return {
        'total_channels': len(df),
        'total_subscribers': df['subscribers'].sum(),
        'total_videos': df['total_videos'].sum(),
        'total_views': df['total_views'].sum(),
        'avg_subscribers': df['subscribers'].mean(),
        'avg_videos_per_channel': df['total_videos'].mean(),
        'avg_views_per_channel': df['total_views'].mean(),
        'median_subscribers': df['subscribers'].median(),
        'top_channel': df.loc[df['subscribers'].idxmax(), 'channel_title'] if len(df) > 0 else 'N/A'
    }

def get_video_summary_stats(df):
    """Generate summary statistics for videos"""
    if df.empty:
        return {
            'total_videos': 0,
            'total_views': 0,
            'total_likes': 0,
            'total_comments': 0,
            'avg_views': 0,
            'avg_engagement_rate': 0,
            'most_viewed_video': 'N/A'
        }
    
    return {
        'total_videos': len(df),
        'total_views': int(df['views'].sum()),
        'total_likes': int(df['likes'].sum()),
        'total_comments': int(df['comments'].sum()),
        'avg_views': int(df['views'].mean()),
        'avg_engagement_rate': float(df['engagement_rate'].mean()),
        'most_viewed_video': df.loc[df['views'].idxmax(), 'title'] if len(df) > 0 else 'N/A',
        'avg_likes': int(df['likes'].mean()),
        'avg_comments': int(df['comments'].mean()),
        'median_views': int(df['views'].median()),
        'top_engagement_video': df.loc[df['engagement_rate'].idxmax(), 'title'] if len(df) > 0 else 'N/A'
    }
