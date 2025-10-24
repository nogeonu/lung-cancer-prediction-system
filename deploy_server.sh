#!/bin/bash

echo "=== 폐암 예측 시스템 서버 배포 스크립트 ==="

# 1. 프로젝트 디렉토리로 이동
cd /home/acorn/lung-cancer-prediction-system

echo "현재 위치: $(pwd)"

# 2. Git 상태 확인
echo "=== Git 상태 확인 ==="
git status
echo ""

# 3. 최신 코드 가져오기
echo "=== 최신 코드 가져오기 ==="
git pull origin main
echo ""

# 4. 데이터베이스 연결 테스트
echo "=== 데이터베이스 연결 테스트 ==="
python3 manage.py shell -c "
from lungcancer.models import LungResult, LungRecord
try:
    results = LungResult.objects.using('heart_db').all()
    records = LungRecord.objects.using('heart_db').all()
    print(f'✅ 외부 DB 연결 성공!')
    print(f'LungResult: {len(results)}개 레코드')
    print(f'LungRecord: {len(records)}개 레코드')
    if results:
        print('최근 결과:')
        for result in results[:3]:
            print(f'  - {result.name} (ID: {result.result_id})')
except Exception as e:
    print(f'❌ 외부 DB 연결 실패: {e}')
    import traceback
    traceback.print_exc()
"
echo ""

# 5. 서비스 재시작
echo "=== 서비스 재시작 ==="
sudo systemctl restart gunicorn
sudo systemctl restart nginx
echo ""

# 6. 서비스 상태 확인
echo "=== 서비스 상태 확인 ==="
sudo systemctl status gunicorn --no-pager -l
echo ""
sudo systemctl status nginx --no-pager -l
echo ""

# 7. 배포 완료 메시지
echo "=== 배포 완료 ==="
echo "서버 URL: http://104.154.212.61:8000/"
echo "환자 관리: http://104.154.212.61:8000/patients/"
echo "데이터 시각화: http://104.154.212.61:8000/visualization/"
echo ""
echo "배포가 완료되었습니다!"
