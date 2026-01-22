from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import os
import requests
from http.cookiejar import MozillaCookieJar
from youtube_transcript_api.proxies import ProxyConfig


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
    proxy_url = os.environ.get("YOUTUBE_PROXY_URL")
    cookies_file = os.environ.get("YOUTUBE_COOKIES_FILE")
    
    proxy_config = None
    http_client = None

    if proxy_url:
        proxy_config = ProxyConfig({"http": proxy_url, "https": proxy_url})

    if cookies_file and os.path.exists(cookies_file):
        http_client = requests.Session()
        http_client.cookies = MozillaCookieJar(cookies_file)
        http_client.cookies.load(ignore_discard=True, ignore_expires=True)

    api = YouTubeTranscriptApi(proxy_config=proxy_config, http_client=http_client)
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
