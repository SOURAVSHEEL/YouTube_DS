"""
Chart and visualization functions
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_channel_comparison_chart(df):
    """Create interactive comparison charts"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Subscribers vs Views', 'Videos vs Subscribers', 
                       'Top Channels by Subscribers', 'Channel Creation Timeline'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Subscribers vs Views
    fig.add_trace(
        go.Scatter(x=df['subscribers'], y=df['total_views'],
                  mode='markers+text', text=df['channel_title'],
                  textposition="top center", name='Channels',
                  marker=dict(size=10, color=df['total_videos'], 
                            colorscale='viridis', showscale=True)),
        row=1, col=1
    )
    
    # Videos vs Subscribers
    fig.add_trace(
        go.Scatter(x=df['total_videos'], y=df['subscribers'],
                  mode='markers+text', text=df['channel_title'],
                  textposition="top center", name='Video Count vs Subs',
                  marker=dict(size=8, color='red')),
        row=1, col=2
    )
    
    # Top channels bar chart
    top_channels = df.nlargest(10, 'subscribers')
    fig.add_trace(
        go.Bar(x=top_channels['channel_title'], y=top_channels['subscribers'],
               name='Top Channels', marker_color='lightblue'),
        row=2, col=1
    )
    
    # Timeline
    if 'created_year' not in df.columns:
        df['created_year'] = pd.to_datetime(df['created_date']).dt.year
    timeline_data = df.groupby('created_year').size().reset_index(name='count')
    fig.add_trace(
        go.Scatter(x=timeline_data['created_year'], y=timeline_data['count'],
                  mode='lines+markers', name='Channels Created',
                  line=dict(color='green', width=3)),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=True, 
                     title_text="YouTube Channel Analytics Dashboard")
    return fig

def create_video_performance_chart(video_df, channel_name):
    """Create video performance visualization"""
    # Calculate engagement rate if it doesn't exist
    if 'engagement_rate' not in video_df.columns:
        video_df = video_df.copy()
        video_df['engagement_rate'] = (video_df['likes'] / video_df['views'].replace(0, 1)) * 100
    
    top_videos = video_df.nlargest(10, 'views')
    
    fig = px.bar(
        top_videos, 
        x='views', 
        y='title',
        orientation='h',
        title=f"Top 10 Videos by Views - {channel_name}",
        labels={'views': 'Views', 'title': 'Video Title'},
        color='engagement_rate',
        color_continuous_scale='viridis',
        hover_data=['likes', 'comments']
    )
    fig.update_layout(height=600)
    return fig

def create_correlation_heatmap(df):
    """Create correlation matrix heatmap"""
    numeric_cols = ['subscribers', 'total_videos', 'total_views']
    corr_matrix = df[numeric_cols].corr()
    
    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                   title="Channel Metrics Correlation Matrix",
                   color_continuous_scale='RdBu_r')
    return fig

def create_engagement_trends_chart(video_df):
    """Create engagement trends over time"""
    # Ensure we have engagement_rate column
    if 'engagement_rate' not in video_df.columns:
        video_df = video_df.copy()
        video_df['engagement_rate'] = (video_df['likes'] / video_df['views'].replace(0, 1)) * 100
    
    # Ensure published_date is datetime
    if not pd.api.types.is_datetime64_any_dtype(video_df['published_date']):
        video_df['published_date'] = pd.to_datetime(video_df['published_date'])
    
    # Group by month
    video_df['month_year'] = video_df['published_date'].dt.to_period('M')
    monthly_stats = video_df.groupby('month_year').agg({
        'views': 'mean',
        'engagement_rate': 'mean',
        'title': 'count'
    }).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=monthly_stats['month_year'].astype(str), 
                  y=monthly_stats['views'],
                  mode='lines+markers', name='Avg Views'),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=monthly_stats['month_year'].astype(str), 
                  y=monthly_stats['engagement_rate'],
                  mode='lines+markers', name='Avg Engagement Rate'),
        secondary_y=True,
    )
    
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Average Views", secondary_y=False)
    fig.update_yaxes(title_text="Engagement Rate (%)", secondary_y=True)
    
    return fig

def create_simple_video_chart(video_df, channel_name):
    """Create a simple video performance chart without engagement rate"""
    top_videos = video_df.nlargest(10, 'views')
    
    fig = px.bar(
        top_videos, 
        x='views', 
        y='title',
        orientation='h',
        title=f"Top 10 Videos by Views - {channel_name}",
        labels={'views': 'Views', 'title': 'Video Title'},
        color='likes',
        color_continuous_scale='blues',
        hover_data=['likes', 'comments']
    )
    fig.update_layout(height=600)
    return fig
