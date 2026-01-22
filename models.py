from pydantic import BaseModel
from typing import List


class SubtitleSegment(BaseModel):
    text: str
    start: float
    duration: float


class SubtitleResponse(BaseModel):
    video_id: str
    language: str
    subtitles: List[SubtitleSegment]
