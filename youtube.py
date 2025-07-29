"""
YouTube API handler module
"""
import streamlit as st
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

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
                part='statistics,snippet',
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
    
    def get_video_transcript(self, video_id, languages=['en', 'hi']):
        """Get video transcript with improved error handling"""
        try:
            # First, validate video ID format
            if not video_id or len(video_id) != 11:
                return {'success': False, 'error': 'Invalid video ID format'}
            
            # Check if video exists and is accessible
            try:
                video_response = self.youtube.videos().list(
                    part='snippet',
                    id=video_id
                ).execute()
                
                if not video_response['items']:
                    return {'success': False, 'error': 'Video not found or is private/deleted'}
            except Exception as e:
                return {'success': False, 'error': f'Cannot access video: {str(e)}'}
            
            # Try to get transcript list
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            except Exception as e:
                error_msg = str(e).lower()
                if 'disabled' in error_msg:
                    return {'success': False, 'error': 'Transcripts are disabled for this video'}
                elif 'not available' in error_msg:
                    return {'success': False, 'error': 'No transcripts available for this video'}
                else:
                    return {'success': False, 'error': f'Cannot retrieve transcript list: {str(e)}'}
            
            # Try to get transcript in preferred languages
            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    transcript_data = transcript.fetch()
                    
                    # Format transcript
                    formatter = TextFormatter()
                    text_formatted = formatter.format_transcript(transcript_data)
                    
                    return {
                        'success': True,
                        'text': text_formatted,
                        'language': lang,
                        'segments': transcript_data
                    }
                except Exception:
                    continue
            
            # If no preferred language found, get the first available
            try:
                available_transcripts = list(transcript_list)
                if available_transcripts:
                    first_transcript = available_transcripts[0]
                    transcript_data = first_transcript.fetch()
                    formatter = TextFormatter()
                    text_formatted = formatter.format_transcript(transcript_data)
                    
                    return {
                        'success': True,
                        'text': text_formatted,
                        'language': first_transcript.language_code,
                        'segments': transcript_data
                    }
            except Exception as e:
                return {'success': False, 'error': f'Failed to fetch available transcript: {str(e)}'}
            
            return {'success': False, 'error': 'No transcripts available in any language'}
            
        except Exception as e:
            error_msg = str(e)
            if 'no element found' in error_msg:
                return {'success': False, 'error': 'Video transcripts are not available or accessible'}
            else:
                return {'success': False, 'error': f'Unexpected error: {error_msg}'}

