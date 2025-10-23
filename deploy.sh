#!/bin/bash

# GCP 자동 배포 스크립트
echo "🚀 GCP 자동 배포 시작..."

# 프로젝트 디렉토리로 이동
cd /home/lung-cancer-app

# Git 최신 코드 가져오기
echo "📥 최신 코드 가져오는 중..."
git pull origin main

# 기존 컨테이너 중지
echo "🛑 기존 컨테이너 중지 중..."
docker-compose down

# 새 이미지 빌드
echo "🔨 새 이미지 빌드 중..."
docker-compose build --no-cache

# 컨테이너 시작
echo "▶️ 컨테이너 시작 중..."
docker-compose up -d

# 배포 완료 확인
echo "✅ 배포 완료!"
echo "🌐 접속 URL: http://104.154.212.61:8000"

# 컨테이너 상태 확인
docker-compose ps
