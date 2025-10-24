# 서버 배포 가이드

## 1. 서버에 SSH 접속
```bash
ssh acorn@104.154.212.61
```

## 2. 프로젝트 디렉토리로 이동
```bash
cd /home/acorn/lung-cancer-prediction-system
```

## 3. 배포 스크립트 실행
```bash
# 배포 스크립트에 실행 권한 부여
chmod +x deploy_server.sh

# 배포 스크립트 실행
./deploy_server.sh
```

## 4. 수동 배포 (스크립트가 안 될 경우)

### 4-1. 최신 코드 가져오기
```bash
git pull origin main
```

### 4-2. 데이터베이스 연결 테스트
```bash
python3 manage.py shell -c "
from lungcancer.models import LungResult, LungRecord
try:
    results = LungResult.objects.using('heart_db').all()
    print(f'외부 DB 연결 성공: {len(results)}개 레코드')
except Exception as e:
    print(f'외부 DB 연결 실패: {e}')
"
```

### 4-3. 서비스 재시작
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### 4-4. 서비스 상태 확인
```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
```

## 5. 배포 확인
- **메인 페이지**: http://104.154.212.61:8000/
- **환자 관리**: http://104.154.212.61:8000/patients/
- **데이터 시각화**: http://104.154.212.61:8000/visualization/

## 6. 문제 해결

### 데이터베이스 연결 실패 시
```bash
# pymysql 설치 확인
pip3 list | grep pymysql

# pymysql 설치 (필요시)
pip3 install pymysql

# Django 설정 확인
python3 manage.py shell -c "
from django.conf import settings
print('데이터베이스 설정:')
for db_name, db_config in settings.DATABASES.items():
    print(f'{db_name}: {db_config[\"HOST\"]}:{db_config[\"PORT\"]}/{db_config[\"NAME\"]}')
"
```

### 서비스 재시작 실패 시
```bash
# 로그 확인
sudo journalctl -u gunicorn -f
sudo journalctl -u nginx -f

# 포트 확인
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :80
```
