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

## 배포 (Deployment)

### GitHub Secrets 설정

GitHub 저장소 설정에서 다음 Secrets를 등록하세요:

| Secret 이름 | 설명 | 예시 |
|------------|------|------|
| `OCI_HOST` | OCI 서버 IP 또는 도메인 | `123.45.67.89` |
| `OCI_USER` | SSH 사용자명 | `ubuntu` 또는 `opc` |
| `OCI_SSH_KEY` | SSH 개인키 전체 내용 | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DEPLOY_PATH` | 서버의 프로젝트 경로 | `/home/ubuntu/youtube-subtitle` |

### 서버 초기 설정

OCI 서버에서 최초 1회만 실행:

```bash
# 프로젝트 클론
git clone https://github.com/your-username/youtube-subtitle.git
cd youtube-subtitle

# nginx-proxy 네트워크 생성 (없는 경우)
docker network create nginx-proxy

# docker-compose.yml의 VIRTUAL_HOST 수정
# your-domain.com을 실제 도메인으로 변경

# 첫 배포
docker-compose up -d
```

### 배포 프로세스

로컬에서 태그 생성 및 푸시:

```bash
# 버전 태그 생성
git tag v1.0.0

# 태그 푸시 (자동 배포 트리거)
git push origin v1.0.0
```

GitHub Actions가 자동으로:
1. OCI 서버에 SSH 접속
2. 최신 태그로 체크아웃
3. Docker 이미지 빌드
4. 컨테이너 재시작
5. 배포 확인

### 배포 확인

```bash
# 서버에서 확인
docker ps
docker logs youtube-subtitle
curl http://localhost:8000/health
```

### 롤백

이전 버전으로 롤백이 필요한 경우:

```bash
# 서버에서 실행
cd /path/to/youtube-subtitle
git checkout v1.0.0  # 이전 태그
docker-compose down
docker-compose up -d --build
```

## 라이선스

MIT License
