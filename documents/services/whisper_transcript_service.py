"""
Service for extracting audio transcripts from YouTube using OpenAI Whisper API.
More reliable than youtube-transcript-api, works on all videos.
"""
import os
import tempfile
import subprocess
from openai import OpenAI
import re
from urllib.parse import urlparse, parse_qs


class WhisperTranscriptService:
    """Extract transcripts using Whisper API."""
    
    @staticmethod
    def extract_video_id(url):
        """Extract video ID from YouTube URL."""
        if not url:
            return None
            
        # Pattern for youtu.be short URLs
        short_pattern = r'youtu\.be/([a-zA-Z0-9_-]+)'
        short_match = re.search(short_pattern, url)
        if short_match:
            return short_match.group(1)
        
        # Pattern for standard YouTube URLs
        parsed_url = urlparse(url)
        if parsed_url.hostname in ['www.youtube.com', 'youtube.com', 'm.youtube.com']:
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                return query_params['v'][0]
        
        return None
    
    @staticmethod
    def parse_timestamp(timestamp_str):
        """
        Convert timestamp string to seconds.
        Supports: "3:45", "1:23:45", "125"
        """
        if not timestamp_str:
            return None
        
        timestamp_str = timestamp_str.strip()
        
        if timestamp_str.isdigit():
            return int(timestamp_str)
        
        parts = timestamp_str.split(':')
        try:
            if len(parts) == 2:  # MM:SS
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            elif len(parts) == 3:  # HH:MM:SS
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            return None
        
        return None
    
    @staticmethod
    def get_transcript(youtube_url, start_time=None, end_time=None):
        """
        Extract transcript from YouTube video using Whisper.
        
        Args:
            youtube_url: Full YouTube URL
            start_time: Start time in seconds (optional)
            end_time: End time in seconds (optional)
        
        Returns:
            dict with 'success', 'text', 'cost_estimate', and optional 'error' keys
        """
        # Get API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {
                'success': False,
                'error': 'OpenAI API key not configured. Please add OPENAI_API_KEY to environment variables.'
            }
        
        # Extract video ID
        video_id = WhisperTranscriptService.extract_video_id(youtube_url)
        if not video_id:
            return {
                'success': False,
                'error': 'Invalid YouTube URL. Please provide a valid YouTube link.'
            }
        
        try:
            # Create temporary directory for audio file
            with tempfile.TemporaryDirectory() as temp_dir:
                audio_file = os.path.join(temp_dir, 'audio.mp3')
                
                # Build yt-dlp command
                cmd = [
                    'yt-dlp',
                    '-x',  # Extract audio only
                    '--audio-format', 'mp3',
                    '-o', audio_file,
                ]
                
                # Add time range if specified
                if start_time is not None or end_time is not None:
                    start = start_time if start_time is not None else 0
                    end = end_time if end_time is not None else 999999
                    cmd.extend(['--download-sections', f'*{start}-{end}'])
                
                cmd.append(f'https://www.youtube.com/watch?v={video_id}')
                
                # Download audio segment
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                if result.returncode != 0:
                    return {
                        'success': False,
                        'error': f'Failed to download audio. The video may be private or unavailable.'
                    }
                
                # Check file exists
                if not os.path.exists(audio_file):
                    return {
                        'success': False,
                        'error': 'Audio file was not created. Please check the video URL.'
                    }
                
                # Get file size for cost estimate
                file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
                
                # Transcribe with Whisper - FORCE ENGLISH LANGUAGE
                client = OpenAI(api_key=api_key)
                with open(audio_file, 'rb') as f:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        language="en",  # Force English - prevents Chinese/wrong language detection
                        response_format="text"
                    )
                
                # Calculate duration estimate (rough: 1MB ≈ 1 minute for MP3)
                duration_minutes = file_size_mb
                cost_estimate = duration_minutes * 0.006
                
                return {
                    'success': True,
                    'text': transcript.strip(),
                    'cost_estimate': round(cost_estimate, 3),
                    'duration_minutes': round(duration_minutes, 1)
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Download timeout. The video segment may be too long.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Transcription error: {str(e)}'
            }