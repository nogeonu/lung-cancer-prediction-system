#!/bin/bash

# GCP 서버에 수동 배포하는 스크립트

echo "🚀 GCP 서버에 폐암 예측 시스템 배포를 시작합니다..."

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

echo ""
echo "🔧 다음 단계를 GCP 서버에서 실행하세요:"
echo ""
echo "1. 이 파일을 GCP 서버에 업로드:"
echo "   scp -i [SSH_KEY] lung-cancer-app.tar shrjsdn908@104.154.212.61:~/"
echo ""
echo "2. GCP 서버에 SSH 접속:"
echo "   ssh -i [SSH_KEY] shrjsdn908@104.154.212.61"
echo ""
echo "3. GCP 서버에서 다음 명령어 실행:"
echo "   # 기존 컨테이너 중지 및 제거"
echo "   docker stop lung-cancer-app || true"
echo "   docker rm lung-cancer-app || true"
echo "   docker rmi lung-cancer-app:latest || true"
echo ""
echo "   # 새 이미지 로드"
echo "   docker load -i lung-cancer-app.tar"
echo ""
echo "   # 새 컨테이너 실행"
echo "   docker run -d \\"
echo "     --name lung-cancer-app \\"
echo "     -p 8000:8000 \\"
echo "     --restart unless-stopped \\"
echo "     lung-cancer-app:latest"
echo ""
echo "   # 정리"
echo "   rm -f lung-cancer-app.tar"
echo ""
echo "4. 배포 확인:"
echo "   curl http://104.154.212.61:8000/"
echo ""
echo "🎉 배포가 완료되면 http://104.154.212.61:8000/ 에서 확인할 수 있습니다!"
