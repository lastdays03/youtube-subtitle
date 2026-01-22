# GitHub Actions 자동 배포 구현 계획

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** OCI 서버에 Docker 컨테이너로 자동 배포하는 GitHub Actions 워크플로우 구축

**Architecture:** Git 태그 생성 시 GitHub Actions가 트리거되어 SSH로 OCI 서버에 접속, 서버에서 직접 Docker 이미지 빌드 및 컨테이너 재시작. nginx-proxy 네트워크를 통해 NPM과 연결.

**Tech Stack:** GitHub Actions, Docker, Docker Compose, SSH (appleboy/ssh-action)

---

## Task 1: Dockerfile 생성

**Files:**
- Create: `Dockerfile`

**Step 1: Dockerfile 작성**

프로젝트 루트에 Dockerfile 생성:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 의존성 먼저 복사하여 레이어 캐싱 최적화
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2: Dockerfile 검증**

로컬에서 Docker 이미지 빌드 테스트:

```bash
docker build -t youtube-subtitle:test .
```

Expected: Successfully built 이미지 ID 출력

**Step 3: 컨테이너 실행 테스트**

```bash
docker run -d -p 8000:8000 --name youtube-subtitle-test youtube-subtitle:test
sleep 3
curl http://localhost:8000/health
docker stop youtube-subtitle-test
docker rm youtube-subtitle-test
docker rmi youtube-subtitle:test
```

Expected: `{"status":"ok"}` 응답

**Step 4: Commit**

```bash
git add Dockerfile
git commit -m "feat: add Dockerfile for containerization"
```

---

## Task 2: docker-compose.yml 생성

**Files:**
- Create: `docker-compose.yml`

**Step 1: docker-compose.yml 작성**

nginx-proxy 네트워크 연결 설정:

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

**Step 2: docker-compose 검증**

로컬에서 테스트 (nginx-proxy 네트워크 없이):

```bash
# 임시로 nginx-proxy 네트워크 생성
docker network create nginx-proxy 2>/dev/null || true

# 컨테이너 시작
docker-compose up -d

# 상태 확인
docker ps | grep youtube-subtitle

# 헬스체크
docker exec youtube-subtitle curl -s http://localhost:8000/health

# 정리
docker-compose down
docker network rm nginx-proxy 2>/dev/null || true
```

Expected: 각 단계에서 정상 출력

**Step 3: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add docker-compose configuration with nginx-proxy network"
```

---

## Task 3: GitHub Actions 워크플로우 생성

**Files:**
- Create: `.github/workflows/deploy.yml`

**Step 1: workflows 디렉토리 생성**

```bash
mkdir -p .github/workflows
```

**Step 2: deploy.yml 작성**

SSH를 통한 자동 배포 워크플로우:

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
      - name: Deploy to OCI server via SSH
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

      - name: Verify deployment
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.OCI_HOST }}
          username: ${{ secrets.OCI_USER }}
          key: ${{ secrets.OCI_SSH_KEY }}
          script: |
            cd ${{ secrets.DEPLOY_PATH }}
            docker ps | grep youtube-subtitle
            docker logs youtube-subtitle --tail 20
```

**Step 3: Commit**

```bash
git add .github/workflows/deploy.yml
git commit -m "feat: add GitHub Actions workflow for OCI deployment"
```

---

## Task 4: README 업데이트

**Files:**
- Modify: `README.md`

**Step 1: README에 배포 섹션 추가**

README.md 파일 끝에 다음 섹션 추가:

```markdown

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
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add deployment instructions to README"
```

---

## Task 5: .dockerignore 생성

**Files:**
- Create: `.dockerignore`

**Step 1: .dockerignore 작성**

Docker 이미지에 불필요한 파일 제외:

```
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
pip-log.txt
pip-delete-this-directory.txt

# Virtual environments
venv/
.venv
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
docs/
*.md
!README.md

# Claude
.claude/

# Worktrees
.worktrees/

# GitHub
.github/
```

**Step 2: Docker 이미지 크기 비교**

.dockerignore 전후 이미지 크기 비교:

```bash
# .dockerignore 적용 후 빌드
docker build -t youtube-subtitle:optimized .
docker images youtube-subtitle:optimized
```

Expected: 이미지 크기 감소 확인

**Step 3: Commit**

```bash
git add .dockerignore
git commit -m "feat: add .dockerignore to optimize Docker image size"
```

---

## Task 6: 서버 배포 가이드 문서 작성

**Files:**
- Create: `docs/DEPLOYMENT.md`

**Step 1: 상세 배포 가이드 작성**

```markdown
# 배포 가이드

## 사전 요구사항

### 서버 환경
- OCI Compute Instance (Ubuntu 20.04 이상)
- Docker 및 Docker Compose 설치됨
- Git 설치됨
- nginx-proxy 네트워크 구성됨

### GitHub 설정
- GitHub 저장소 접근 권한
- Secrets 설정 완료

## 초기 서버 설정

### 1. 프로젝트 클론

```bash
cd /home/ubuntu  # 또는 원하는 경로
git clone https://github.com/your-username/youtube-subtitle.git
cd youtube-subtitle
```

### 2. nginx-proxy 네트워크 확인/생성

```bash
# 네트워크 존재 확인
docker network ls | grep nginx-proxy

# 없으면 생성
docker network create nginx-proxy
```

### 3. 환경 설정

docker-compose.yml 파일 수정:

```bash
nano docker-compose.yml
```

`VIRTUAL_HOST`를 실제 도메인으로 변경:
```yaml
environment:
  - VIRTUAL_HOST=subtitle.yourdomain.com
  - VIRTUAL_PORT=8000
```

### 4. 첫 배포

```bash
docker-compose up -d
```

### 5. 배포 확인

```bash
# 컨테이너 상태
docker ps

# 로그 확인
docker logs youtube-subtitle

# 헬스체크
docker exec youtube-subtitle curl -s http://localhost:8000/health
```

## 일반 배포 프로세스

### 1. 로컬에서 태그 생성

```bash
# 버전 업데이트
git tag v1.0.1

# 태그 푸시
git push origin v1.0.1
```

### 2. GitHub Actions 확인

- GitHub 저장소 → Actions 탭
- 배포 워크플로우 실행 확인
- 약 2-3분 소요

### 3. 배포 확인

서버에서 확인:

```bash
ssh user@your-server
cd /home/ubuntu/youtube-subtitle
docker ps
docker logs youtube-subtitle --tail 50
```

## 트러블슈팅

### 컨테이너가 시작되지 않는 경우

```bash
# 로그 확인
docker logs youtube-subtitle

# 컨테이너 재시작
docker-compose restart

# 완전 재빌드
docker-compose down
docker-compose up -d --build
```

### GitHub Actions 실패

1. Actions 탭에서 로그 확인
2. Secrets 값 확인
3. 서버 SSH 접근 확인:
   ```bash
   ssh -i your-key.pem user@server-ip
   ```

### 네트워크 연결 문제

```bash
# 네트워크 확인
docker network inspect nginx-proxy

# 컨테이너가 네트워크에 연결되었는지 확인
docker inspect youtube-subtitle | grep -A 10 Networks
```

### 롤백

```bash
cd /home/ubuntu/youtube-subtitle
git fetch --tags
git checkout v1.0.0  # 이전 버전
docker-compose down
docker-compose up -d --build
```

## 모니터링

### 컨테이너 상태

```bash
docker ps -a
docker stats youtube-subtitle
```

### 로그 확인

```bash
# 실시간 로그
docker logs youtube-subtitle -f

# 최근 100줄
docker logs youtube-subtitle --tail 100
```

### 디스크 공간 관리

```bash
# 사용하지 않는 이미지 정리
docker system prune -a

# 특정 이미지만 삭제
docker images
docker rmi <image-id>
```

## 보안 고려사항

1. SSH 키는 GitHub Secrets에만 보관
2. 정기적인 패키지 업데이트:
   ```bash
   docker-compose pull
   docker-compose up -d
   ```
3. 방화벽 설정 (80, 443만 허용)
4. 정기적인 백업

## NPM 설정

Nginx Proxy Manager에서:

1. Proxy Hosts → Add Proxy Host
2. Details:
   - Domain Names: `subtitle.yourdomain.com`
   - Scheme: `http`
   - Forward Hostname/IP: `youtube-subtitle` (컨테이너 이름)
   - Forward Port: `8000`
3. SSL 탭에서 Let's Encrypt 인증서 발급
4. Save

## 유지보수

### 정기 작업

- 주간: 로그 확인 및 정리
- 월간: 디스크 공간 확인 및 정리
- 분기: 보안 업데이트 확인

### 백업

```bash
# docker-compose.yml 백업
cp docker-compose.yml docker-compose.yml.backup

# 환경 설정 백업
docker inspect youtube-subtitle > container-config.json
```
```

**Step 2: Commit**

```bash
git add docs/DEPLOYMENT.md
git commit -m "docs: add detailed deployment guide"
```

---

## Task 7: 최종 검증 및 문서화

**Step 1: 모든 파일 존재 확인**

```bash
ls -la Dockerfile
ls -la docker-compose.yml
ls -la .dockerignore
ls -la .github/workflows/deploy.yml
ls -la docs/DEPLOYMENT.md
```

Expected: 모든 파일 존재

**Step 2: Git 상태 확인**

```bash
git status
git log --oneline -7
```

Expected: 7개의 새 커밋, working tree clean

**Step 3: 최종 정리 커밋 (필요시)**

```bash
git add .
git status
# 변경사항이 있으면 커밋
```

**Step 4: 브랜치 푸시 준비**

작업 완료 후 메인 브랜치로 머지하기 위한 준비:

```bash
# 모든 커밋 확인
git log main..feature/github-actions-deploy --oneline

# 변경된 파일 목록
git diff main --name-only
```

Expected: 다음 파일들이 변경됨
- Dockerfile
- docker-compose.yml
- .dockerignore
- .github/workflows/deploy.yml
- README.md
- docs/DEPLOYMENT.md

---

## 검증 체크리스트

구현 완료 후 확인:

- [ ] Dockerfile 생성 및 로컬 빌드 성공
- [ ] docker-compose.yml 생성 및 로컬 실행 성공
- [ ] .dockerignore 생성
- [ ] GitHub Actions 워크플로우 파일 생성
- [ ] README.md에 배포 섹션 추가
- [ ] docs/DEPLOYMENT.md 상세 가이드 작성
- [ ] 모든 커밋 완료 (7개)
- [ ] Git 상태 clean

## 배포 후 작업

1. **GitHub Secrets 설정**
   - 저장소 Settings → Secrets and variables → Actions
   - OCI_HOST, OCI_USER, OCI_SSH_KEY, DEPLOY_PATH 등록

2. **서버 초기 설정**
   - 프로젝트 클론
   - nginx-proxy 네트워크 생성
   - docker-compose.yml의 VIRTUAL_HOST 수정
   - 첫 배포 실행

3. **첫 태그 배포 테스트**
   - `git tag v0.1.0`
   - `git push origin v0.1.0`
   - GitHub Actions 실행 확인
   - 서버에서 배포 확인

## 참고

- Docker 이미지 크기: 약 150-200MB
- 배포 소요 시간: 2-3분
- 다운타임: 5-10초
