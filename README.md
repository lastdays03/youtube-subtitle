# YouTube Subtitle API

YouTube 비디오 ID로 자막을 추출하는 가벼운 Python 기반 웹서버입니다. LLM 분석에 적합한 JSON 형식으로 타임스탬프를 포함한 자막 데이터를 제공합니다.

## 특징

- ✨ 간단한 REST API
- 🔍 자동 언어 감지
- ⏱️ 타임스탬프 포함 (LLM 분석 최적화)
- 🚀 빠르고 가벼운 구현
- 📝 자동 API 문서화 (Swagger UI)
- 🔑 YouTube API 키 불필요

## 기술 스택

- **웹 프레임워크:** FastAPI
- **자막 라이브러리:** youtube-transcript-api
- **서버:** uvicorn

## 설치 방법

### 1. 저장소 클론

```bash
cd youtube-subtitle
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면 다음 주소로 접속할 수 있습니다:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 사용법

### 1. Health Check

서버 상태를 확인합니다.

```bash
curl http://localhost:8000/health
```

**응답:**
```json
{
  "status": "ok"
}
```

### 2. 자막 추출

YouTube 비디오 ID로 자막을 추출합니다.

```bash
curl http://localhost:8000/subtitle/dQw4w9WgXcQ
```

**성공 응답 (200):**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "ko",
  "subtitles": [
    {
      "text": "자막 텍스트",
      "start": 0.0,
      "duration": 2.5
    },
    {
      "text": "다음 자막",
      "start": 2.5,
      "duration": 3.0
    }
  ]
}
```

**에러 응답:**

- **404 - 자막 없음:**
```json
{
  "detail": "No subtitles found for video: VIDEO_ID"
}
```

- **404 - 비디오 없음:**
```json
{
  "detail": "Video not found or unavailable: VIDEO_ID"
}
```

- **500 - 서버 오류:**
```json
{
  "detail": "Internal server error"
}
```

## 프로젝트 구조

```
youtube-subtitle/
├── main.py              # FastAPI 애플리케이션 진입점
├── services.py          # 자막 추출 비즈니스 로직
├── models.py            # Pydantic 응답 스키마
├── requirements.txt     # 의존성 패키지
└── README.md           # 프로젝트 문서
```

## API 엔드포인트

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | 서버 상태 확인 |
| GET | `/subtitle/{video_id}` | 자막 추출 |

## 예시

### Python으로 사용하기

```python
import requests

# 자막 추출
response = requests.get("http://localhost:8000/subtitle/dQw4w9WgXcQ")
data = response.json()

print(f"언어: {data['language']}")
for subtitle in data['subtitles']:
    print(f"[{subtitle['start']:.2f}s] {subtitle['text']}")
```

### JavaScript로 사용하기

```javascript
fetch('http://localhost:8000/subtitle/dQw4w9WgXcQ')
  .then(response => response.json())
  .then(data => {
    console.log(`언어: ${data.language}`);
    data.subtitles.forEach(sub => {
      console.log(`[${sub.start}s] ${sub.text}`);
    });
  });
```

## 특성

- **응답 시간:** 1-3초 (YouTube API 호출)
- **메모리 사용량:** ~50MB (매우 가벼움)
- **동시 처리:** uvicorn의 비동기 처리로 다중 요청 지원

## 라이선스

MIT License
