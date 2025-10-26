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
        Supports: "3:45", "1:23:45", "125", or integer
        """
        if not timestamp_str:
            return None
        
        # If already an integer, return it
        if isinstance(timestamp_str, int):
            return timestamp_str
        
        # Convert to string if needed
        timestamp_str = str(timestamp_str).strip()
        
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
    def get_youtube_transcript(video_id, start_seconds=None, end_seconds=None):
        """
        Try to get transcript from YouTube's captions (free, no download).
        Returns dict with 'success', 'text', and optional 'error'.
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            # Configure proxy if available
            proxy_url = os.getenv('PROXY_URL')
            api = None

            if proxy_url:
                from youtube_transcript_api.proxies import GenericProxyConfig
                proxy_config = GenericProxyConfig(
                    http_url=proxy_url,
                    https_url=proxy_url
                )
                api = YouTubeTranscriptApi(proxy_config=proxy_config)
            else:
                api = YouTubeTranscriptApi()

            # Fetch the transcript using the correct API for v1.2.2
            fetched_transcript = api.fetch(video_id)
            transcript_list = fetched_transcript.to_raw_data()

            # Filter by time range if specified
            if start_seconds is not None and end_seconds is not None:
                filtered_text = []
                for entry in transcript_list:
                    entry_start = entry['start']
                    entry_end = entry['start'] + entry['duration']

                    # Include if entry overlaps with our time range
                    if entry_end >= start_seconds and entry_start <= end_seconds:
                        filtered_text.append(entry['text'])

                full_text = ' '.join(filtered_text)
            else:
                # No time filter - get all text
                full_text = ' '.join([entry['text'] for entry in transcript_list])

            return {
                'success': True,
                'text': full_text.strip(),
                'method': 'youtube_transcript'
            }

        except Exception as e:
            # Log more details for debugging
            import logging
            logging.error(f"YouTube transcript fetch failed for video {video_id}: {str(e)}")
            logging.error(f"Proxy configured: {os.getenv('PROXY_URL') is not None}")

            return {
                'success': False,
                'error': f'No YouTube transcript available: {str(e)}',
                'method': 'youtube_transcript'
            }


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
        
        start_seconds = WhisperTranscriptService.parse_timestamp(start_time) if start_time else None
        end_seconds = WhisperTranscriptService.parse_timestamp(end_time) if end_time else None

    # TRY YOUTUBE TRANSCRIPT FIRST
        youtube_result = WhisperTranscriptService.get_youtube_transcript(video_id, start_seconds, end_seconds)
        if youtube_result['success']:
            # Calculate duration
            if start_seconds is not None and end_seconds is not None:
                duration_minutes = (end_seconds - start_seconds) / 60.0
            else:
                duration_minutes = 0
            
            return {
                'success': True,
                'text': youtube_result['text'],
                'cost_estimate': 0.0,
                'duration_minutes': round(duration_minutes, 1)
            }
        try:
            # Create temporary directory for audio file
            with tempfile.TemporaryDirectory() as temp_dir:
                audio_file = os.path.join(temp_dir, 'audio.mp3')
                
                # Build yt-dlp command with retry options
                cmd = [
                    'yt-dlp',
                    '-x',  # Extract audio only
                    '--audio-format', 'mp3',
                    '-o', audio_file,
                    '--retries', '5',              # Retry up to 5 times
                    '--fragment-retries', '5',      # Retry fragments 5 times
                    '--socket-timeout', '30',       # 30 second socket timeout
                ]

                # Add proxy if configured
                proxy_url = os.getenv('PROXY_URL')
                if proxy_url:
                    cmd.extend(['--proxy', proxy_url])
                
                # Add time range if specified
                if start_time is not None or end_time is not None:
                    start = start_time if start_time is not None else 0
                    end = end_time if end_time is not None else 999999
                    cmd.extend(['--download-sections', f'*{start}-{end}'])
                
                cmd.append(f'https://www.youtube.com/watch?v={video_id}')
                
                # Download audio segment
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                if result.returncode != 0:
                    # Log error details for debugging
                    import logging
                    logging.error(f"yt-dlp failed for video {video_id}")
                    logging.error(f"Command: {' '.join(cmd)}")
                    logging.error(f"stdout: {result.stdout}")
                    logging.error(f"stderr: {result.stderr}")
                    logging.error(f"Proxy configured: {proxy_url is not None}")

                    return {
                        'success': False,
                        'error': f'Failed to download audio. The video may be private or unavailable. Error: {result.stderr[:200]}'
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