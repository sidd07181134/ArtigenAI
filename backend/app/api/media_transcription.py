"""
Media Transcription API endpoints

Endpoints for transcribing YouTube videos using Groq Whisper and ingesting into Qdrant.
All endpoints require admin authentication.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_current_active_admin
from app.models.database import get_db
from app.models.schemas import (
    YouTubeTranscriptionRequest,
    YouTubeTranscriptionResponse,
    MediaHealthResponse,
    DocumentIngest
)
from app.services.media_transcription_service import (
    transcribe_youtube_url,
    extract_youtube_video_id,
    TranscriptionError,
    get_groq_client
)
from app.services.ingestion_service import ingestion_service
from app.services.vector_service import vector_service
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/media", tags=["media-transcription"])

# Log router initialization
logger.info("Media transcription router initialized with prefix: /api/media")


@router.post("/youtube/transcribe", response_model=YouTubeTranscriptionResponse)
async def youtube_transcribe(
    payload: YouTubeTranscriptionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_admin)
):
    """
    Transcribe a YouTube video and ingest the transcript into Qdrant.
    
    Flow:
    1. Validate YouTube URL and extract video ID
    2. Download audio from YouTube
    3. Transcribe audio using Groq Whisper (whisper-large-v3)
    4. Ingest transcript into Qdrant using existing ingestion pipeline
    5. Return preview and status
    
    Legal & Compliance:
    - Admin-only access (enforced via auth)
    - Only process content you have the right to analyze
    - Must comply with YouTube Terms of Service
    """
    url = payload.url.strip()
    
    try:
        # Step 1: Extract video ID (validates URL format)
        video_id = extract_youtube_video_id(url)
        logger.info(f"Transcribing YouTube video: {video_id}")
        
        # Step 2 & 3: Download and transcribe
        transcript = transcribe_youtube_url(url)
        
        if not transcript or not transcript.strip():
            raise HTTPException(
                status_code=500,
                detail="Empty transcript returned from audio transcription"
            )
        
        logger.info(f"Transcription completed: {len(transcript)} characters")
        
        # Step 4: Ingest into Qdrant using existing ingestion pipeline
        try:
            document_data = DocumentIngest(
                title=f"YouTube Video: {video_id}",
                source="youtube",
                url=url,
                content=transcript,
                metadata={
                    "source_type": "media",
                    "platform": "youtube",
                    "youtube_video_id": video_id,
                }
            )
            
            ingested_doc = ingestion_service.ingest_document(
                db=db,
                document_data=document_data,
                origin_id=None  # Media transcriptions don't have an origin
            )
            
            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            tokens_ingested = len(transcript) // 4
            
            logger.info(f"Successfully ingested YouTube transcript: document ID {ingested_doc.id}")
            
            # Step 5: Return preview and status
            preview = transcript[:500] if len(transcript) > 500 else transcript
            
            return YouTubeTranscriptionResponse(
                success=True,
                message=f"Transcription and ingestion completed successfully. Document ID: {ingested_doc.id}",
                preview=preview,
                tokens_ingested=tokens_ingested
            )
            
        except Exception as ingest_error:
            logger.exception(f"Ingestion failed for YouTube video {video_id}: {ingest_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to ingest transcript into Qdrant: {str(ingest_error)}"
            )
    
    except ValueError as ve:
        # Invalid URL format
        logger.warning(f"Invalid YouTube URL: {url} - {ve}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid YouTube URL: {str(ve)}"
        )
    
    except TranscriptionError as te:
        # Transcription failed
        logger.error(f"Transcription failed for {url}: {te}")
        raise HTTPException(
            status_code=502,
            detail=f"Transcription failed: {str(te)}"
        )
    
    except Exception as e:
        logger.exception(f"Unexpected error transcribing YouTube video: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/health", response_model=MediaHealthResponse)
async def get_media_health(
    current_user = Depends(get_current_active_admin)
):
    """
    Get health status of media transcription services.
    
    Checks:
    - Groq API connectivity and configuration
    - Qdrant connection status
    """
    health_status: dict = {
        "groq_api": {"status": "error", "message": "Not checked"},
        "qdrant": {"status": "error", "message": "Not checked", "connected": False},
        "overall_status": "unhealthy"
    }
    
    # Check Groq API
    try:
        if not settings.groq_api_key or not settings.groq_api_key.strip():
            health_status["groq_api"] = {
                "status": "error",
                "message": "Groq API key not configured"
            }
        else:
            # Try to create a client (doesn't make an API call, just validates config)
            client = get_groq_client()
            health_status["groq_api"] = {
                "status": "ok",
                "message": "Groq API key configured"
            }
    except Exception as e:
        health_status["groq_api"] = {
            "status": "error",
            "message": f"Groq API check failed: {str(e)}"
        }
    
    # Check Qdrant
    try:
        # Use existing vector service to check Qdrant connection
        if vector_service.client:
            # Try to get collection info (lightweight check)
            try:
                collections = vector_service.client.get_collections()
                collections_count = len(collections.collections) if hasattr(collections, 'collections') else 0
                health_status["qdrant"] = {
                    "status": "ok",
                    "message": "Qdrant connected",
                    "connected": True,
                    "collections_count": collections_count
                }
            except Exception as qe:
                health_status["qdrant"] = {
                    "status": "error",
                    "message": f"Qdrant connection error: {str(qe)}",
                    "connected": False
                }
        else:
            health_status["qdrant"] = {
                "status": "error",
                "message": "Qdrant client not initialized",
                "connected": False
            }
    except Exception as e:
        health_status["qdrant"] = {
            "status": "error",
            "message": f"Qdrant health check failed: {str(e)}",
            "connected": False
        }
    
    # Determine overall status
    groq_ok = health_status["groq_api"]["status"] == "ok"
    qdrant_ok = health_status["qdrant"]["status"] == "ok"
    
    if groq_ok and qdrant_ok:
        health_status["overall_status"] = "healthy"
    elif groq_ok or qdrant_ok:
        health_status["overall_status"] = "degraded"
    else:
        health_status["overall_status"] = "unhealthy"
    
    return MediaHealthResponse(**health_status)

