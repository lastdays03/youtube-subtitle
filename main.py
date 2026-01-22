from fastapi import FastAPI, HTTPException
from services import get_subtitle
from models import SubtitleResponse
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

app = FastAPI(
    title="YouTube Subtitle API",
    description="YouTube 비디오의 자막을 추출하는 API",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}


@app.get("/subtitle/{video_id}", response_model=SubtitleResponse)
def get_video_subtitle(video_id: str):
    """
    YouTube 비디오 ID로 자막을 추출합니다.

    Args:
        video_id: YouTube 비디오 ID

    Returns:
        SubtitleResponse: 비디오 ID, 언어, 자막 데이터를 포함한 응답

    Raises:
        HTTPException: 자막을 찾을 수 없거나 비디오를 사용할 수 없는 경우
    """
    try:
        return get_subtitle(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        raise HTTPException(
            status_code=404,
            detail=f"No subtitles found for video: {video_id}"
        )
    except VideoUnavailable:
        raise HTTPException(
            status_code=404,
            detail=f"Video not found or unavailable: {video_id}"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
