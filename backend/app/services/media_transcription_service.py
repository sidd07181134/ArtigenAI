"""
Media Transcription Service

This service handles YouTube video transcription using Groq Whisper API.
It downloads audio from YouTube videos and transcribes them using Groq's whisper-large-v3 model.

Legal & Compliance Notes:
- This service is for internal/admin use only
- Only process content you have the right to analyze
- Must comply with YouTube Terms of Service
- No DRM circumvention or unauthorized content processing
"""

import os
import tempfile
import logging
from typing import Tuple
from urllib.parse import urlparse, parse_qs
from groq import Groq
from app.core.config import settings

try:
    import yt_dlp
except ImportError:
    yt_dlp = None
    logger = logging.getLogger(__name__)
    logger.warning("yt_dlp not installed. YouTube transcription will not work. Install with: pip install yt-dlp")

logger = logging.getLogger(__name__)


class TranscriptionError(Exception):
    """Custom exception for transcription errors"""
    pass


def get_groq_client() -> Groq:
    """
    Get or create Groq client instance.
    Reuses the same configuration as the RAG service.
    """
    if not settings.groq_api_key or not settings.groq_api_key.strip():
        raise TranscriptionError("Groq API key not configured")
    
    return Groq(api_key=settings.groq_api_key)


def extract_youtube_video_id(url: str) -> str:
    """
    Extract YouTube video ID from various URL formats.
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    
    Args:
        url: YouTube URL string
        
    Returns:
        Video ID string
        
    Raises:
        ValueError: If URL is not a valid YouTube URL or video ID cannot be extracted
    """
    parsed = urlparse(url)
    
    # Handle youtube.com/watch?v=VIDEO_ID format
    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        vid = qs.get("v", [None])[0]
        if not vid:
            raise ValueError("No video ID (v=) found in YouTube URL")
        return vid
    
    # Handle youtu.be/VIDEO_ID format
    if "youtu.be" in parsed.netloc:
        vid = parsed.path.lstrip("/")
        if not vid:
            raise ValueError("No video ID found in youtu.be URL")
        return vid
    
    raise ValueError("URL is not a supported YouTube link format")


def download_youtube_audio(url: str) -> Tuple[str, str]:
    """
    Download audio-only stream from YouTube into a temporary file.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Tuple of (file_path, file_basename)
        
    Raises:
        TranscriptionError: If download fails
    """
    if yt_dlp is None:
        raise TranscriptionError("yt_dlp is not installed. Please install it with: pip install yt-dlp")
    
    tmp_dir = tempfile.mkdtemp(prefix="yt_audio_")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(tmp_dir, "%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
        return filename, os.path.basename(filename)
    except Exception as e:
        logger.error(f"Failed to download YouTube audio: {e}")
        raise TranscriptionError(f"Failed to download audio from YouTube: {str(e)}")


def transcribe_with_groq(audio_path: str, original_name: str) -> str:
    """
    Use Groq Whisper (whisper-large-v3) to transcribe the audio file.
    
    Args:
        audio_path: Path to the audio file
        original_name: Original filename for the API
        
    Returns:
        Transcript text string
        
    Raises:
        TranscriptionError: If transcription fails
    """
    try:
        client = get_groq_client()
        
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        
        logger.info(f"Transcribing audio file: {original_name} ({len(audio_data)} bytes)")
        
        transcription = client.audio.transcriptions.create(
            file=(original_name, audio_data),
            model="whisper-large-v3",
            temperature=0,
            response_format="verbose_json",
        )
        
        # Extract text from response
        # Groq returns a TranscriptionVerboseResponse object with a 'text' attribute
        text = getattr(transcription, "text", None)
        
        if not text:
            # Fallback: try to access as dict-like
            if hasattr(transcription, "__dict__"):
                text = transcription.__dict__.get("text")
            if not text:
                raise TranscriptionError("No text returned from Groq transcription")
        
        logger.info(f"Transcription completed: {len(text)} characters")
        return text
        
    except Exception as exc:
        logger.error(f"Groq transcription failed: {exc}")
        raise TranscriptionError(f"Groq transcription failed: {str(exc)}") from exc


def transcribe_youtube_url(url: str) -> str:
    """
    High-level function to transcribe a YouTube video.
    
    Flow:
    1. Validate and extract video ID from URL
    2. Download audio to temporary file
    3. Transcribe using Groq Whisper
    4. Clean up temporary files
    5. Return transcript text
    
    Args:
        url: YouTube video URL
        
    Returns:
        Transcript text string
        
    Raises:
        ValueError: If URL is invalid
        TranscriptionError: If download or transcription fails
    """
    video_id = None
    audio_path = None
    
    try:
        # Step 1: Extract video ID
        video_id = extract_youtube_video_id(url)
        logger.info(f"Extracted video ID: {video_id}")
        
        # Step 2: Download audio
        audio_path, basename = download_youtube_audio(url)
        logger.info(f"Downloaded audio to: {audio_path}")
        
        # Step 3: Transcribe
        transcript = transcribe_with_groq(audio_path, basename)
        
        return transcript
        
    finally:
        # Step 4: Clean up temporary files
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                # Also try to remove the temp directory if empty
                tmp_dir = os.path.dirname(audio_path)
                if os.path.exists(tmp_dir):
                    try:
                        os.rmdir(tmp_dir)
                    except OSError:
                        pass  # Directory not empty or other error, ignore
            except OSError as e:
                logger.warning(f"Failed to clean up temp file {audio_path}: {e}")

