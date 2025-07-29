"""
YouTube API handler module - Public Data Only
"""
import streamlit as st
from googleapiclient.discovery import build

class YouTubeAnalytics:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        
    def search_channels(self, query, max_results=50):
        """Search for channels based on query"""
        try:
            search_response = self.youtube.search().list(
                q=query,
                part='snippet',
                type='channel',
                maxResults=max_results,
                relevanceLanguage='en'
            ).execute()
            
            channels = []
            for item in search_response['items']:
                channels.append({
                    'channel_id': item['snippet']['channelId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'][:200] + '...',
                    'thumbnail': item['snippet']['thumbnails']['default']['url']
                })
            return channels
        except Exception as e:
            st.error(f"Error searching channels: {str(e)}")
            return []
    
    def get_channel_stats(self, channel_ids):
        """Get detailed channel statistics"""
        all_data = []
        
        # Split channel_ids into chunks of 50 (API limit)
        for i in range(0, len(channel_ids), 50):
            chunk = channel_ids[i:i+50]
            
            request = self.youtube.channels().list(
                part='snippet,contentDetails,statistics',
                id=','.join(chunk)
            )
            response = request.execute()
            
            for item in response['items']:
                data = {
                    'channel_id': item['id'],
                    'channel_title': item['snippet']['title'],
                    'created_date': item['snippet']['publishedAt'],
                    'description': item['snippet']['description'][:300] + '...',
                    'country': item['snippet'].get('country', 'Not specified'),
                    'subscribers': int(item['statistics'].get('subscriberCount', 0)),
                    'total_videos': int(item['statistics'].get('videoCount', 0)),
                    'total_views': int(item['statistics'].get('viewCount', 0)),
                    'playlist_id': item['contentDetails']['relatedPlaylists']['uploads']
                }
                all_data.append(data)
        
        return all_data
    
    def get_video_details(self, playlist_id, max_results=50):
        """Get video details from a channel's playlist"""
        videos = []
        next_page_token = None
        
        while len(videos) < max_results:
            request = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            )
            response = request.execute()
            
            video_ids = []
            for item in response['items']:
                video_ids.append(item['snippet']['resourceId']['videoId'])
            
            # Get video statistics
            stats_request = self.youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=','.join(video_ids)
            )
            stats_response = stats_request.execute()
            
            for item in stats_response['items']:
                video_data = {
                    'video_id': item['id'],
                    'title': item['snippet']['title'],
                    'published_date': item['snippet']['publishedAt'],
                    'views': int(item['statistics'].get('viewCount', 0)),
                    'likes': int(item['statistics'].get('likeCount', 0)),
                    'comments': int(item['statistics'].get('commentCount', 0)),
                    'duration': item.get('contentDetails', {}).get('duration', 'N/A')
                }
                videos.append(video_data)
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
        return videos
