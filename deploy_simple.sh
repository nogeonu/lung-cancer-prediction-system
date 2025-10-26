#!/bin/bash

echo "🚀 간단한 GCP 배포 스크립트를 시작합니다..."

# 1. Docker 이미지 빌드
echo "📦 Docker 이미지를 빌드합니다..."
docker build -t lung-cancer-app .

if [ $? -ne 0 ]; then
    echo "❌ Docker 이미지 빌드 실패"
    exit 1
fi

# 2. Docker 이미지를 tar 파일로 저장
echo "💾 Docker 이미지를 tar 파일로 저장합니다..."
docker save -o lung-cancer-app.tar lung-cancer-app:latest

if [ $? -ne 0 ]; then
    echo "❌ Docker 이미지 저장 실패"
    exit 1
fi

echo "✅ Docker 이미지가 성공적으로 빌드되고 저장되었습니다!"
echo "📁 파일 크기: $(ls -lh lung-cancer-app.tar | awk '{print $5}')"

# 3. rsync를 사용해서 파일 전송 시도
echo "📤 rsync를 사용해서 GCP 서버에 파일을 전송합니다..."

# 여러 SSH 키로 rsync 시도
SSH_KEYS=(
    "~/.ssh/gcp_key"
    "~/.ssh/gcp_deploy_key"
    "~/.ssh/gcp_manual_deploy"
    "~/.ssh/google_compute_engine"
    "~/.ssh/gcp_final_key"
)

for key in "${SSH_KEYS[@]}"; do
    echo "🔑 SSH 키 시도: $key"
    if rsync -avz -e "ssh -i $key -o ConnectTimeout=10 -o StrictHostKeyChecking=no" \
        lung-cancer-app.tar shrjsdn908@104.154.212.61:~/ 2>/dev/null; then
        echo "✅ 파일 전송 성공! SSH 키: $key"
        
        # SSH로 배포 명령어 실행
        echo "🚀 GCP 서버에서 배포를 시작합니다..."
        ssh -i "$key" -o ConnectTimeout=10 -o StrictHostKeyChecking=no shrjsdn908@104.154.212.61 << 'EOF'
            echo "📋 기존 컨테이너 중지 및 제거..."
            docker stop lung-cancer-app || true
            docker rm lung-cancer-app || true
            docker rmi lung-cancer-app:latest || true
            
            echo "📥 새 이미지 로드..."
            docker load -i lung-cancer-app.tar
            
            echo "🚀 새 컨테이너 실행..."
            docker run -d \
                --name lung-cancer-app \
                -p 8000:8000 \
                --restart unless-stopped \
                lung-cancer-app:latest
            
            echo "🧹 정리 작업..."
            rm -f lung-cancer-app.tar
            
            echo "⏳ 컨테이너 시작 대기..."
            sleep 15
            
            echo "🔍 배포 상태 확인..."
            docker ps | grep lung-cancer-app
            
            echo "🌐 서비스 테스트..."
            curl -f http://localhost:8000/ && echo "✅ 배포 성공!" || echo "❌ 배포 실패"
EOF
        
        if [ $? -eq 0 ]; then
            echo "🎉 배포가 완료되었습니다!"
            echo "🌐 http://104.154.212.61:8000/ 에서 확인하세요!"
            exit 0
        else
            echo "❌ 배포 실패"
        fi
    else
        echo "❌ SSH 키 $key 로 접속 실패"
    fi
done

echo "❌ 모든 SSH 키로 접속 실패. 수동 배포를 진행하세요."
echo ""
echo "📋 수동 배포 명령어:"
echo "1. 파일 전송: scp -i [SSH_KEY] lung-cancer-app.tar shrjsdn908@104.154.212.61:~/"
echo "2. SSH 접속: ssh -i [SSH_KEY] shrjsdn908@104.154.212.61"
echo "3. 배포 실행:"
echo "   docker stop lung-cancer-app || true"
echo "   docker rm lung-cancer-app || true"
echo "   docker rmi lung-cancer-app:latest || true"
echo "   docker load -i lung-cancer-app.tar"
echo "   docker run -d --name lung-cancer-app -p 8000:8000 --restart unless-stopped lung-cancer-app:latest"
echo "   rm -f lung-cancer-app.tar"
