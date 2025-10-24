#!/bin/bash

echo "=== Docker 기반 폐암 예측 시스템 배포 스크립트 ==="

# 1. 프로젝트 디렉토리로 이동
cd ~/lung-cancer-prediction-system
echo "현재 위치: $(pwd)"

# 2. Git 상태 확인
echo "=== Git 상태 확인 ==="
git status
echo ""

# 3. 최신 코드 가져오기
echo "=== 최신 코드 가져오기 ==="
git pull origin main
echo ""

# 4. Docker 컨테이너 중지
echo "=== Docker 컨테이너 중지 ==="
sudo docker-compose down
echo ""

# 5. Docker 컨테이너 재시작
echo "=== Docker 컨테이너 재시작 ==="
sudo docker-compose up -d
echo ""

# 6. 컨테이너 상태 확인
echo "=== 컨테이너 상태 확인 ==="
sudo docker-compose ps
echo ""

# 7. 로그 확인
echo "=== 최근 로그 확인 ==="
sudo docker-compose logs --tail=20
echo ""

# 8. 웹사이트 접속 테스트
echo "=== 웹사이트 접속 테스트 ==="
curl -I http://localhost:8000
echo ""

# 9. 배포 완료 메시지
echo "=== 배포 완료 ==="
echo "서버 URL: http://104.154.212.61:8000/"
echo "환자 관리: http://104.154.212.61:8000/patients/"
echo "데이터 시각화: http://104.154.212.61:8000/visualization/"
echo ""
echo "배포가 완료되었습니다!"
