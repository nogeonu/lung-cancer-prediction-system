# 🚀 GCP 자동 배포 설정 가이드

## 📋 **필요한 준비사항**

### 1. GCP VM 인스턴스 설정
```bash
# GCP VM에 접속
gcloud compute ssh your-instance-name --zone=your-zone

# 필요한 패키지 설치
sudo apt update
sudo apt install -y docker.io docker-compose git

# Docker 서비스 시작
sudo systemctl start docker
sudo systemctl enable docker

# 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
```

### 2. 프로젝트 클론
```bash
# 홈 디렉토리에 프로젝트 클론
cd /home
git clone https://github.com/nogeonu/lung-cancer-prediction-system.git lung-cancer-app
cd lung-cancer-app
```

### 3. GitHub Secrets 설정
GitHub 저장소 Settings → Secrets and variables → Actions에서 다음 시크릿 추가:

- `GCP_HOST`: 104.154.212.61
- `GCP_USERNAME`: GCP VM 사용자명
- `GCP_SSH_KEY`: GCP VM SSH 개인키

### 4. 방화벽 설정
```bash
# GCP 콘솔에서 방화벽 규칙 생성
# 포트 8000 허용
gcloud compute firewall-rules create allow-django-app \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Django app on port 8000"
```

## 🔄 **자동 배포 워크플로우**

### GitHub Actions 트리거
- `main` 브랜치에 push할 때마다 자동 배포
- Pull Request 생성 시 테스트 실행

### 배포 과정
1. **코드 체크아웃**: GitHub에서 최신 코드 가져오기
2. **의존성 설치**: Python 패키지 설치
3. **테스트 실행**: Django 테스트 실행
4. **GCP 배포**: SSH로 GCP VM에 접속하여 배포
5. **컨테이너 재시작**: Docker 컨테이너 재빌드 및 시작

## 🌐 **접속 방법**

배포 완료 후 다음 URL로 접속:
- **메인 페이지**: http://104.154.212.61:8000
- **관리자 페이지**: http://104.154.212.61:8000/admin

## 🛠️ **수동 배포 (필요시)**

GCP VM에서 직접 배포:
```bash
cd /home/lung-cancer-app
./deploy.sh
```

## 📊 **모니터링**

### 컨테이너 상태 확인
```bash
docker-compose ps
docker-compose logs -f
```

### 로그 확인
```bash
# 애플리케이션 로그
docker-compose logs web

# 실시간 로그 모니터링
docker-compose logs -f web
```

## 🔧 **문제 해결**

### 포트 충돌 시
```bash
# 포트 사용 중인 프로세스 확인
sudo netstat -tlnp | grep :8000

# 프로세스 종료
sudo kill -9 <PID>
```

### 컨테이너 재시작
```bash
docker-compose restart web
```

### 완전 재배포
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```
