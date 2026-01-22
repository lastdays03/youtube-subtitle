from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)


def get_subtitle(video_id: str):
    """
    YouTube 비디오 ID로 자막을 추출합니다.

    Args:
        video_id: YouTube 비디오 ID

    Returns:
        dict: video_id, language, subtitles를 포함한 딕셔너리

    Raises:
        TranscriptsDisabled: 자막이 비활성화된 경우
        NoTranscriptFound: 자막을 찾을 수 없는 경우
        VideoUnavailable: 비디오를 사용할 수 없는 경우
    """
    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id)

    # FetchedTranscript 객체에서 데이터 추출
    subtitles = [
        {
            "text": snippet.text,
            "start": snippet.start,
            "duration": snippet.duration
        }
        for snippet in fetched.snippets
    ]

    return {
        "video_id": fetched.video_id,
        "language": fetched.language_code,
        "subtitles": subtitles
    }
