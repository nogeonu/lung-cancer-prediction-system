#!/bin/bash

# 🚀 GCP 서버 초기 설정 스크립트
# 이 스크립트는 GCP VM에서 최초 1회만 실행합니다.

echo "=================================="
echo "🚀 GCP 서버 자동 배포 환경 설정"
echo "=================================="
echo ""

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 현재 사용자 확인
CURRENT_USER=$(whoami)
echo "📌 현재 사용자: $CURRENT_USER"
echo ""

# 1. 시스템 업데이트
echo "1️⃣ 시스템 업데이트 중..."
sudo apt update && sudo apt upgrade -y
echo -e "${GREEN}✅ 시스템 업데이트 완료${NC}"
echo ""

# 2. Docker 설치
echo "2️⃣ Docker 설치 확인 중..."
if ! command -v docker &> /dev/null; then
    echo "Docker가 설치되어 있지 않습니다. 설치를 시작합니다..."
    sudo apt install -y docker.io
    echo -e "${GREEN}✅ Docker 설치 완료${NC}"
else
    echo -e "${GREEN}✅ Docker가 이미 설치되어 있습니다.${NC}"
fi
echo ""

# 3. Docker Compose 설치
echo "3️⃣ Docker Compose 설치 확인 중..."
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose가 설치되어 있지 않습니다. 설치를 시작합니다..."
    sudo apt install -y docker-compose
    echo -e "${GREEN}✅ Docker Compose 설치 완료${NC}"
else
    echo -e "${GREEN}✅ Docker Compose가 이미 설치되어 있습니다.${NC}"
fi
echo ""

# 4. Git 설치
echo "4️⃣ Git 설치 확인 중..."
if ! command -v git &> /dev/null; then
    echo "Git이 설치되어 있지 않습니다. 설치를 시작합니다..."
    sudo apt install -y git
    echo -e "${GREEN}✅ Git 설치 완료${NC}"
else
    echo -e "${GREEN}✅ Git이 이미 설치되어 있습니다.${NC}"
fi
echo ""

# 5. Docker 서비스 시작
echo "5️⃣ Docker 서비스 설정 중..."
sudo systemctl start docker
sudo systemctl enable docker
echo -e "${GREEN}✅ Docker 서비스 활성화 완료${NC}"
echo ""

# 6. 사용자를 docker 그룹에 추가
echo "6️⃣ 사용자를 Docker 그룹에 추가 중..."
sudo usermod -aG docker $CURRENT_USER
echo -e "${GREEN}✅ Docker 그룹 추가 완료${NC}"
echo -e "${YELLOW}⚠️  변경사항 적용을 위해 로그아웃 후 다시 로그인해주세요.${NC}"
echo ""

# 7. 프로젝트 디렉토리 확인 및 생성
echo "7️⃣ 프로젝트 디렉토리 설정 중..."
PROJECT_DIR="/home/lung-cancer-app"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  프로젝트 디렉토리가 이미 존재합니다.${NC}"
    read -p "기존 디렉토리를 삭제하고 새로 클론하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "기존 디렉토리 삭제 중..."
        sudo rm -rf $PROJECT_DIR
    else
        echo "기존 디렉토리를 유지합니다."
        PROJECT_DIR="$PROJECT_DIR-$(date +%Y%m%d%H%M%S)"
        echo "새 디렉토리: $PROJECT_DIR"
    fi
fi

echo "GitHub 저장소 클론 중..."
cd /home
sudo git clone https://github.com/nogeonu/lung-cancer-prediction-system.git lung-cancer-app
sudo chown -R $CURRENT_USER:$CURRENT_USER $PROJECT_DIR
echo -e "${GREEN}✅ 프로젝트 클론 완료${NC}"
echo ""

# 8. SSH 키 설정 안내
echo "8️⃣ SSH 키 설정 안내"
echo "=================================="
echo "GitHub Actions에서 자동 배포를 위해 SSH 키가 필요합니다."
echo ""
echo "🔑 SSH 키 생성 (아직 생성하지 않았다면):"
echo "   ssh-keygen -t rsa -b 4096 -C \"your-email@example.com\""
echo ""
echo "📋 공개키 확인 및 등록:"
echo "   cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys"
echo "   chmod 600 ~/.ssh/authorized_keys"
echo ""
echo "📤 개인키를 GitHub Secrets에 등록:"
echo "   로컬에서: cat ~/.ssh/id_rsa"
echo "   GitHub: Settings → Secrets → GCP_SSH_KEY에 등록"
echo ""

# 9. 방화벽 설정 안내
echo "9️⃣ 방화벽 설정 안내"
echo "=================================="
echo "GCP 콘솔에서 포트 8000을 열어야 합니다."
echo ""
echo "명령어로 방화벽 규칙 생성:"
echo "   gcloud compute firewall-rules create allow-django-app \\"
echo "       --allow tcp:8000 \\"
echo "       --source-ranges 0.0.0.0/0 \\"
echo "       --description \"Allow Django app on port 8000\""
echo ""
echo "또는 GCP 콘솔에서:"
echo "   VPC 네트워크 → 방화벽 규칙 → 규칙 만들기"
echo "   포트: tcp:8000"
echo "   소스: 0.0.0.0/0"
echo ""

# 10. 초기 배포 실행
echo "🔟 초기 배포 실행"
echo "=================================="
read -p "지금 초기 배포를 실행하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "초기 배포 시작..."
    cd $PROJECT_DIR
    chmod +x deploy.sh
    ./deploy.sh
    echo -e "${GREEN}✅ 초기 배포 완료${NC}"
else
    echo "나중에 수동으로 배포하려면:"
    echo "   cd $PROJECT_DIR"
    echo "   ./deploy.sh"
fi
echo ""

# 완료 메시지
echo "=================================="
echo -e "${GREEN}🎉 설정 완료!${NC}"
echo "=================================="
echo ""
echo "📝 다음 단계:"
echo "   1. 로그아웃 후 다시 로그인 (Docker 그룹 권한 적용)"
echo "   2. GitHub Secrets 설정:"
echo "      - GCP_HOST: 104.154.212.61"
echo "      - GCP_USERNAME: $CURRENT_USER"
echo "      - GCP_SSH_KEY: SSH 개인키 내용"
echo "   3. GCP 방화벽에서 포트 8000 열기"
echo "   4. main 브랜치에 푸시하면 자동 배포 시작!"
echo ""
echo "🌐 배포 후 접속 URL: http://104.154.212.61:8000"
echo ""
echo "📚 자세한 내용은 GCP_AUTO_DEPLOY.md 파일을 참고하세요."
echo ""

