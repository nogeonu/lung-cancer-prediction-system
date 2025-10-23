# 🚀 GitHub → GCP 자동 배포 가이드

## 📌 개요
이 프로젝트는 GitHub Actions를 사용하여 코드를 푸시할 때마다 자동으로 GCP 서버(104.154.212.61)에 배포됩니다.

## 🎯 자동 배포 흐름

```
팀원이 코드 수정
    ↓
GitHub에 Push (main 브랜치)
    ↓
GitHub Actions 자동 실행
    ↓
GCP 서버에 SSH 접속
    ↓
최신 코드 다운로드
    ↓
Docker 컨테이너 재빌드
    ↓
서비스 재시작
    ↓
✅ 배포 완료!
```

## ⚙️ 초기 설정 (관리자만 1회 실행)

### 1️⃣ GCP VM 서버 설정

GCP VM에 SSH로 접속:
```bash
gcloud compute ssh your-instance-name --zone=your-zone
```

필요한 패키지 설치:
```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
sudo apt install -y docker.io docker-compose git

# Docker 서비스 시작
sudo systemctl start docker
sudo systemctl enable docker

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# 세션 재로그인 (또는 재부팅)
exit
```

다시 접속 후 프로젝트 클론:
```bash
cd /home
sudo git clone https://github.com/nogeonu/lung-cancer-prediction-system.git lung-cancer-app
sudo chown -R $USER:$USER /home/lung-cancer-app
cd lung-cancer-app
```

### 2️⃣ GitHub Secrets 설정

GitHub 저장소에서 **Settings** → **Secrets and variables** → **Actions** → **New repository secret** 클릭

다음 3개의 Secret을 추가:

#### 📝 `GCP_HOST`
```
104.154.212.61
```

#### 📝 `GCP_USERNAME`
```
# GCP VM의 사용자명 (보통 이메일 앞부분)
# 예: nogeonu 또는 your-email-username
```

사용자명 확인 방법:
```bash
# GCP VM에서 실행
whoami
```

#### 📝 `GCP_SSH_KEY`

SSH 개인키 생성 및 등록:

**로컬 컴퓨터에서:**
```bash
# SSH 키 생성 (이미 있으면 생략)
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
# 엔터 3번 (기본 경로, 비밀번호 없음)

# 개인키 내용 확인 및 복사
cat ~/.ssh/id_rsa
```

출력된 전체 내용을 복사 (-----BEGIN ... END----- 포함)

**GCP VM에서:**
```bash
# 공개키 내용 확인 및 복사
cat ~/.ssh/id_rsa.pub

# authorized_keys에 공개키 추가
echo "복사한_공개키_내용" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3️⃣ GCP 방화벽 설정

GCP 콘솔에서 또는 명령어로 포트 8000 열기:

```bash
gcloud compute firewall-rules create allow-django-app \
    --allow tcp:8000 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow Django app on port 8000"
```

또는 GCP 콘솔에서:
1. **VPC 네트워크** → **방화벽 규칙**
2. **방화벽 규칙 만들기**
3. 이름: `allow-django-app`
4. 대상: 네트워크의 모든 인스턴스
5. 소스 IP 범위: `0.0.0.0/0`
6. 프로토콜 및 포트: `tcp:8000`
7. 만들기 클릭

## 🔄 사용 방법 (팀원용)

### 1. 코드 수정 후 푸시

```bash
# 코드 수정 후
git add .
git commit -m "기능 추가 또는 버그 수정"
git push origin main
```

### 2. 자동 배포 확인

GitHub 저장소에서:
1. **Actions** 탭 클릭
2. 최근 워크플로우 실행 확인
3. 진행 상황 실시간 모니터링

### 3. 배포 완료 후 확인

브라우저에서 접속:
```
http://104.154.212.61:8000
```

## 📊 배포 상태 확인

### GitHub에서 확인
- **Actions** 탭에서 배포 상태 확인
- 성공: ✅ 녹색 체크마크
- 실패: ❌ 빨간색 X 표시

### GCP 서버에서 확인
```bash
# SSH로 접속
ssh your-username@104.154.212.61

# 프로젝트 디렉토리 이동
cd /home/lung-cancer-app

# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 최근 로그만 확인
docker-compose logs --tail=50 web
```

## 🔧 수동 배포 (필요시)

GitHub Actions가 실패하거나 긴급 배포가 필요한 경우:

```bash
# GCP VM에 SSH 접속
ssh your-username@104.154.212.61

# 배포 스크립트 실행
cd /home/lung-cancer-app
chmod +x deploy.sh
./deploy.sh
```

또는 GitHub에서 수동 트리거:
1. **Actions** 탭
2. **🚀 GCP 자동 배포** 워크플로우 선택
3. **Run workflow** 버튼 클릭
4. **Run workflow** 확인

## ⚠️ 주의사항

### ✅ 해야 할 것
- `main` 브랜치에 푸시하기 전에 로컬에서 테스트
- 의미 있는 커밋 메시지 작성
- 큰 변경사항은 Pull Request로 리뷰 후 병합

### ❌ 하지 말아야 할 것
- `main` 브랜치에 직접 푸시할 때는 신중하게
- 테스트하지 않은 코드 푸시 금지
- 민감한 정보(API 키, 비밀번호 등) 코드에 포함 금지

## 🐛 문제 해결

### 1. 배포가 실패하는 경우

**GitHub Actions 로그 확인:**
```
Actions 탭 → 실패한 워크플로우 클릭 → 오류 메시지 확인
```

**일반적인 오류:**
- SSH 연결 실패: Secrets 설정 확인
- Docker 빌드 실패: requirements.txt 확인
- 포트 충돌: GCP VM에서 포트 확인

### 2. 서비스가 응답하지 않는 경우

```bash
# GCP VM에서 실행
cd /home/lung-cancer-app

# 컨테이너 상태 확인
docker-compose ps

# 컨테이너가 실행 중이 아니면 재시작
docker-compose up -d

# 로그 확인
docker-compose logs --tail=100 web
```

### 3. 포트 충돌 해결

```bash
# 포트 8000 사용 중인 프로세스 확인
sudo netstat -tlnp | grep :8000

# 프로세스 종료 (PID 확인 후)
sudo kill -9 <PID>

# 또는 Docker 컨테이너 재시작
docker-compose restart
```

### 4. 완전 재배포

```bash
# GCP VM에서 실행
cd /home/lung-cancer-app

# 모든 컨테이너와 이미지 삭제
docker-compose down
docker system prune -af

# 최신 코드 다운로드
git fetch origin
git reset --hard origin/main

# 재빌드 및 시작
docker-compose build --no-cache
docker-compose up -d
```

## 📞 연락처

문제가 해결되지 않으면 관리자에게 연락:
- GitHub Issues에 문제 등록
- 또는 팀 채팅방에 문의

## 🎓 추가 학습 자료

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Docker 공식 문서](https://docs.docker.com/)
- [Django 배포 가이드](https://docs.djangoproject.com/en/stable/howto/deployment/)

---

**🌟 Happy Coding! 🌟**

