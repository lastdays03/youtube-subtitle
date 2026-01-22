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
