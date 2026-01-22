# GitHub Actions 자동 배포 설계

**작성일:** 2026-01-22
**대상 서버:** OCI
**배포 방식:** Docker + nginx-proxy 네트워크

## 개요

YouTube Subtitle API를 OCI 서버에 자동 배포하는 CI/CD 파이프라인 구축. Git 태그 생성 시 GitHub Actions가 트리거되어 서버에서 Docker 이미지를 빌드하고 컨테이너를 재시작합니다.

## 아키텍처

### 배포 흐름

1. 개발자가 Git 태그 생성 (예: `v1.0.0`)
2. GitHub Actions가 자동으로 트리거됨
3. SSH로 OCI 서버에 접속
4. 서버에서 Git pull로 최신 코드 가져오기
5. 서버에서 Docker 이미지 빌드
6. 기존 컨테이너 중지 및 제거
7. 새 컨테이너 시작 (nginx-proxy 네트워크에 연결)
8. NPM이 도메인을 통해 새 컨테이너로 트래픽 라우팅

### 네트워크 구조

```
Internet → NPM (Nginx Proxy Manager) → nginx-proxy network → youtube-subtitle container
```

- 외부 포트 노출 없음
- nginx-proxy 네트워크를 통해 NPM과 통신
- VIRTUAL_HOST 환경변수로 도메인 매핑

## GitHub Secrets 설정

다음 Secrets를 GitHub 저장소에 등록해야 합니다:

| Secret 이름 | 설명 | 예시 |
|------------|------|------|
| `OCI_HOST` | 서버 IP 또는 도메인 | `123.45.67.89` |
| `OCI_USER` | SSH 사용자명 | `ubuntu` 또는 `opc` |
| `OCI_SSH_KEY` | SSH 개인키 전체 내용 | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DEPLOY_PATH` | 서버의 프로젝트 경로 | `/home/ubuntu/youtube-subtitle` |

## 파일 구조

### 1. Dockerfile

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**특징:**
- `python:3.9-slim`: 가벼운 Python 이미지
- 레이어 캐싱 최적화: requirements.txt 먼저 복사
- `--no-cache-dir`: 이미지 크기 감소
- 포트 8000 노출

### 2. docker-compose.yml

```yaml
version: '3.8'
services:
  youtube-subtitle:
    build: .
    container_name: youtube-subtitle
    restart: unless-stopped
    environment:
      - VIRTUAL_HOST=your-domain.com
      - VIRTUAL_PORT=8000
    networks:
      - nginx-proxy

networks:
  nginx-proxy:
    external: true
```

**환경변수:**
- `VIRTUAL_HOST`: NPM에서 사용할 도메인
- `VIRTUAL_PORT`: 컨테이너 내부 포트
- `restart: unless-stopped`: 서버 재부팅 시 자동 시작

### 3. GitHub Actions Workflow

**.github/workflows/deploy.yml:**

```yaml
name: Deploy to OCI Server

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.OCI_HOST }}
          username: ${{ secrets.OCI_USER }}
          key: ${{ secrets.OCI_SSH_KEY }}
          script: |
            cd ${{ secrets.DEPLOY_PATH }}
            git fetch --tags
            git checkout ${{ github.ref_name }}
            docker-compose down
            docker-compose build --no-cache
            docker-compose up -d
```

**워크플로우 설명:**
- `on.push.tags`: v로 시작하는 태그에만 트리거
- `appleboy/ssh-action`: SSH 연결 및 명령 실행
- `--no-cache`: 항상 최신 코드로 빌드
- `-d`: 백그라운드 실행

## 서버 초기 설정

최초 1회만 서버에서 수동으로 실행:

```bash
# 1. 프로젝트 클론
cd /home/ubuntu
git clone https://github.com/your-username/youtube-subtitle.git
cd youtube-subtitle

# 2. nginx-proxy 네트워크 생성 (없는 경우)
docker network create nginx-proxy

# 3. 첫 배포
docker-compose up -d
```

## 배포 프로세스

### 정상 배포

```bash
# 로컬에서 태그 생성 및 푸시
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions가 자동으로 배포 진행
# 약 2-3분 소요 (빌드 시간 포함)
```

### 배포 확인

```bash
# 서버에서 확인
docker ps -a                    # 컨테이너 상태
docker logs youtube-subtitle    # 로그 확인
```

## 에러 처리

### 로그 확인

```bash
docker logs youtube-subtitle
docker logs youtube-subtitle --tail 100
docker logs youtube-subtitle -f  # 실시간
```

### 컨테이너 재시작

```bash
docker-compose restart
```

### 완전 재배포

```bash
docker-compose down
docker-compose up -d --build
```

### 롤백

이전 버전으로 롤백:

```bash
cd /home/ubuntu/youtube-subtitle
git checkout v1.0.0  # 이전 태그
docker-compose down
docker-compose up -d --build
```

## 무중단 배포 고려사항

현재 설계는 간단한 배포 방식으로 짧은 다운타임(5-10초)이 발생합니다.

**다운타임 발생 지점:**
- `docker-compose down`: 기존 컨테이너 중지
- `docker-compose build`: 이미지 빌드 (1-2분)
- `docker-compose up -d`: 새 컨테이너 시작

**향후 개선 방안:**
- Blue-Green 배포: 두 개의 컨테이너를 번갈아 사용
- Health check 추가: 새 컨테이너가 준비된 후 전환
- 현재는 트래픽이 적어 간단한 방식으로 충분

## 보안 고려사항

1. **SSH 키 관리**
   - GitHub Secrets에 저장 (암호화됨)
   - 읽기 전용 권한으로 제한 권장

2. **환경변수**
   - 민감한 정보는 docker-compose.yml에 직접 입력하지 않음
   - 필요시 `.env` 파일 사용 (git에 커밋하지 않음)

3. **네트워크 격리**
   - nginx-proxy 네트워크만 사용
   - 외부 포트 직접 노출하지 않음

## 모니터링

### 컨테이너 상태 확인

```bash
docker ps -a
docker stats youtube-subtitle
```

### 애플리케이션 상태 확인

```bash
# Health check endpoint
curl http://localhost:8000/health
```

## 참고 사항

- **빌드 시간**: 첫 빌드는 2-3분, 캐시 활용 시 30초-1분
- **재시작 시간**: 5-10초
- **로그 보관**: Docker 기본 설정 (제한 없음, 추후 logrotate 설정 권장)
- **디스크 공간**: 오래된 이미지는 `docker system prune -a`로 정리
