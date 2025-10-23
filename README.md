# 🫁 폐암 조기 진단 지원 시스템

머신러닝 기반 폐암 예측 및 환자 관리 웹 애플리케이션

[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.2-orange.svg)](https://scikit-learn.org/)

---

## 📋 목차

- [프로젝트 개요](#-프로젝트-개요)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [모델 성능](#-모델-성능)
- [설치 및 실행](#-설치-및-실행)
- [프로젝트 구조](#-프로젝트-구조)
- [페이지 구조](#-페이지-구조)
- [데이터베이스 모델](#-데이터베이스-모델)
- [입력 특성](#-입력-특성)
- [사용 가이드](#-사용-가이드)
- [관리자 기능](#-관리자-기능)
- [모델 재학습](#-모델-재학습)
- [주의사항](#-주의사항)

---

## 🎯 프로젝트 개요

이 프로젝트는 **Django**와 **머신러닝**을 활용하여 환자의 증상 정보로부터 폐암 발병 위험도를 예측하는 웹 시스템입니다. 의료진의 진단 보조 도구로 활용될 수 있으며, 환자 데이터 관리 및 통계 분석 기능을 제공합니다.

### 핵심 가치

- ✅ **조기 진단 지원**: 15개 특성을 기반으로 폐암 위험도를 빠르게 평가
- ✅ **환자 관리**: 체계적인 환자 정보 관리 시스템
- ✅ **데이터 시각화**: 직관적인 차트와 그래프로 데이터 분석
- ✅ **사용자 친화적**: Bootstrap 5 기반의 깔끔한 UI/UX

---

## 🚀 주요 기능

### 1. 폐암 예측 시스템
- 15개 특성(증상, 생활습관)을 입력받아 폐암 발병 위험도 예측
- Random Forest 알고리즘 기반 예측 (정확도 91.94%)
- 위험도 수준별 시각적 피드백 (낮음/중간/높음)
- 예측 확률 및 권장 사항 제공

### 2. 환자 관리 (CRUD)
- **생성(Create)**: 신규 환자 정보 입력 및 자동 예측
- **조회(Read)**: 환자 목록 및 상세 정보 확인
- **수정(Update)**: 환자 정보 수정 및 자동 재예측
- **삭제(Delete)**: 환자 정보 안전 삭제 (확인 절차 포함)

### 3. 데이터 시각화
- 📊 예측 결과 분포 (파이 차트)
- 📈 연령대별 폐암 예측 분포 (바 차트)
- 👥 성별 폐암 예측 분포 (바 차트)
- 📉 예측 확률 분포 (히스토그램)
- 📌 통계 정보 요약 (총 환자 수, 양성/음성 비율, 평균 연령 등)

### 4. 사용자 인증 시스템
- 회원가입 및 로그인
- 로그아웃
- 비밀번호 변경
- 세션 기반 인증

### 5. 공지사항 관리
- 관리자가 공지사항 작성 및 삭제
- 중요 공지 강조 표시
- 홈 페이지에 최신 공지 표시

### 6. Q&A 시스템
- 로그인 없이 질문 작성 가능
- 카테고리별 질문 분류
- 관리자 답변 기능
- 답변 완료/대기 상태 관리

### 7. 관리자 페이지
- Django Admin을 통한 데이터 관리
- 환자, 공지사항, Q&A 통합 관리
- 필터링, 검색, 정렬 기능

---

## 🛠 기술 스택

### Backend
- **Django 4.2.7**: 웹 프레임워크
- **SQLite3**: 데이터베이스
- **Python 3.9+**: 프로그래밍 언어

### Machine Learning
- **scikit-learn 1.3.2**: Random Forest Classifier
- **pandas 2.1.3**: 데이터 처리
- **numpy 1.24.3**: 수치 연산
- **joblib 1.3.2**: 모델 직렬화

### Data Visualization
- **matplotlib 3.8.2**: 차트 생성
- **seaborn 0.13.0**: 통계 시각화

### Frontend
- **Bootstrap 5**: UI 프레임워크
- **Bootstrap Icons**: 아이콘
- **HTML5/CSS3**: 마크업

---

## 📊 모델 성능

### 모델 정보
- **알고리즘**: Random Forest Classifier
- **학습 데이터**: 309개 환자 샘플 (survey lung cancer.csv)
- **테스트 데이터**: 20% 홀드아웃 (계층화 샘플링)
- **정확도**: **91.94%**
- **입력 특성**: 15개

### 주요 특성 중요도

| 순위 | 특성 | 중요도 |
|------|------|--------|
| 1 | ALLERGY (알레르기) | 15.09% |
| 2 | ALCOHOL CONSUMING (음주) | 11.26% |
| 3 | PEER_PRESSURE (또래 압박) | 9.60% |
| 4 | AGE (나이) | 9.33% |
| 5 | WHEEZING (쌕쌕거림) | 7.34% |

### 모델 하이퍼파라미터
- `n_estimators`: 100
- `max_depth`: 10
- `min_samples_split`: 5
- `min_samples_leaf`: 2
- `class_weight`: balanced
- `random_state`: 42

---

## 💻 설치 및 실행

### 1️⃣ 가상환경 활성화

```bash
cd "/Users/nogeon-u/Desktop/건양대_바이오메디컬 /Django/Django_project"
source venv/bin/activate
```

### 2️⃣ 패키지 설치 (처음 실행 시)

```bash
pip install -r requirements.txt
```

### 3️⃣ 데이터베이스 마이그레이션 (처음 실행 시)

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4️⃣ 슈퍼유저 생성 (선택사항)

관리자 페이지 및 관리자 기능 사용을 위해 슈퍼유저를 생성합니다:

```bash
python manage.py createsuperuser
```

### 5️⃣ 서버 실행

```bash
python manage.py runserver
```

### 6️⃣ 브라우저에서 접속

```
http://127.0.0.1:8000/
```

---

## 📁 프로젝트 구조

```
Django_project/
│
├── lungcancer/                    # 메인 애플리케이션
│   ├── migrations/               # 데이터베이스 마이그레이션 파일
│   │   ├── 0001_initial.py
│   │   └── 0002_notice_qna_alter...py
│   │
│   ├── ml_model/                 # 머신러닝 모델 저장소
│   │   ├── lung_cancer_model.pkl      # 학습된 Random Forest 모델
│   │   └── feature_names.pkl          # 특성 이름 리스트
│   │
│   ├── templates/                # HTML 템플릿
│   │   ├── lungcancer/
│   │   │   ├── base.html              # 기본 레이아웃
│   │   │   ├── home.html              # 홈 페이지
│   │   │   ├── predict.html           # 예측 입력 폼
│   │   │   ├── result.html            # 예측 결과
│   │   │   ├── patient_list.html      # 환자 목록
│   │   │   ├── patient_detail.html    # 환자 상세
│   │   │   ├── patient_update.html    # 환자 수정
│   │   │   ├── patient_delete.html    # 환자 삭제 확인
│   │   │   ├── visualization.html     # 데이터 시각화
│   │   │   ├── change_password.html   # 비밀번호 변경
│   │   │   ├── qna_list.html          # Q&A 목록
│   │   │   ├── qna_ask.html           # 질문 작성
│   │   │   └── qna_answer.html        # 답변 작성 (관리자)
│   │   │
│   │   └── registration/
│   │       ├── login.html             # 로그인
│   │       └── signup.html            # 회원가입
│   │
│   ├── admin.py                  # Django Admin 설정
│   ├── apps.py                   # 앱 구성
│   ├── forms.py                  # Django 폼 (PatientForm)
│   ├── models.py                 # 데이터 모델 (Patient, Notice, QnA)
│   ├── views.py                  # 뷰 로직
│   ├── urls.py                   # URL 라우팅
│   ├── train_model.py            # 모델 학습 스크립트
│   └── data_preprocessing.py     # 데이터 전처리 (예비용)
│
├── lungcancer_project/            # 프로젝트 설정
│   ├── settings.py               # Django 설정 파일
│   ├── urls.py                   # 메인 URL 설정
│   ├── wsgi.py                   # WSGI 설정
│   └── asgi.py                   # ASGI 설정
│
├── static/                        # 정적 파일
│   ├── css/
│   │   └── home.css              # 커스텀 CSS
│   └── img/
│       └── 폐암_이미지.jpeg        # 이미지 리소스
│
├── venv/                          # Python 가상환경
│
├── manage.py                      # Django 관리 스크립트
├── requirements.txt               # Python 패키지 의존성
├── survey lung cancer.csv         # 학습 데이터셋
├── lung_cancer_model_training.ipynb  # 모델 개발 노트북
├── 폐암_머신러닝_모델.ipynb         # 모델 분석 노트북
├── db.sqlite3                     # SQLite 데이터베이스
└── README.md                      # 프로젝트 문서 (현재 파일)
```

---

## 🌐 페이지 구조

### 공개 페이지

| URL | 이름 | 설명 |
|-----|------|------|
| `/` | 홈 | 시스템 개요, 통계 정보, 공지사항, Q&A |
| `/login/` | 로그인 | 사용자 로그인 |
| `/signup/` | 회원가입 | 신규 사용자 등록 |
| `/qna/` | Q&A 목록 | 질문과 답변 목록 |
| `/qna/ask/` | 질문 작성 | 로그인 없이 질문 작성 가능 |

### 인증 필요 페이지

| URL | 이름 | 설명 |
|-----|------|------|
| `/logout/` | 로그아웃 | 로그아웃 처리 |
| `/change-password/` | 비밀번호 변경 | 비밀번호 변경 폼 |
| `/predict/` | 예측하기 | 환자 증상 입력 및 예측 |
| `/result/<id>/` | 예측 결과 | 개별 예측 결과 표시 |
| `/patients/` | 환자 목록 | 모든 환자 정보 조회 |
| `/patients/<id>/` | 환자 상세 | 개별 환자 상세 정보 |
| `/patients/<id>/update/` | 환자 수정 | 환자 정보 수정 및 재예측 |
| `/patients/<id>/delete/` | 환자 삭제 | 환자 정보 삭제 확인 |
| `/visualization/` | 데이터 시각화 | 차트 및 통계 정보 |

### 관리자 전용 페이지

| URL | 이름 | 설명 |
|-----|------|------|
| `/admin/` | 관리자 페이지 | Django Admin 인터페이스 |
| `/add-notice/` | 공지사항 추가 | 새 공지사항 작성 |
| `/delete-notice/<id>/` | 공지사항 삭제 | 공지사항 삭제 (AJAX) |
| `/qna/<id>/answer/` | 답변 작성 | Q&A 답변 작성 |

---

## 🗃 데이터베이스 모델

### 1. Patient (환자)

환자의 기본 정보, 증상, 예측 결과를 저장합니다.

**필드:**
- `id`: 기본키 (자동 증가)
- `gender`: 성별 (1=남성, 0=여성)
- `age`: 나이
- `smoking`: 흡연 여부 (2=예, 1=아니오)
- `yellow_fingers`: 손가락 변색
- `anxiety`: 불안
- `peer_pressure`: 또래 압박
- `chronic_disease`: 만성 질환
- `fatigue`: 피로
- `allergy`: 알레르기
- `wheezing`: 쌕쌕거림
- `alcohol_consuming`: 음주
- `coughing`: 기침
- `shortness_of_breath`: 호흡 곤란
- `swallowing_difficulty`: 삼킴 곤란
- `chest_pain`: 가슴 통증
- `prediction`: 예측 결과 ('YES' / 'NO')
- `prediction_probability`: 예측 확률 (0.0 ~ 1.0)
- `created_at`: 등록일 (자동)
- `updated_at`: 수정일 (자동)

### 2. Notice (공지사항)

시스템 공지사항을 관리합니다.

**필드:**
- `id`: 기본키
- `title`: 제목
- `content`: 내용
- `is_important`: 중요 공지 여부
- `is_active`: 활성화 여부
- `created_at`: 등록일
- `updated_at`: 수정일

### 3. QnA (질문과 답변)

사용자 질문과 관리자 답변을 관리합니다.

**필드:**
- `id`: 기본키
- `question`: 질문 내용
- `answer`: 답변 내용
- `category`: 카테고리
- `is_answered`: 답변 완료 여부
- `is_active`: 활성화 여부
- `questioner_name`: 질문자 이름
- `questioner_email`: 질문자 이메일
- `created_at`: 등록일
- `updated_at`: 수정일

---

## 🔬 입력 특성

### 특성 목록 및 설명

| 순번 | 특성명 | 한글명 | 값 | 설명 |
|------|--------|--------|-----|------|
| 1 | GENDER | 성별 | 1=남성, 0=여성 | 환자의 생물학적 성별 |
| 2 | AGE | 나이 | 숫자 | 환자의 연령 (세) |
| 3 | SMOKING | 흡연 | 2=예, 1=아니오 | 흡연 습관 여부 |
| 4 | YELLOW_FINGERS | 손가락 변색 | 2=예, 1=아니오 | 니코틴에 의한 손가락 변색 |
| 5 | ANXIETY | 불안 | 2=예, 1=아니오 | 불안 증상 경험 여부 |
| 6 | PEER_PRESSURE | 또래 압박 | 2=예, 1=아니오 | 또래 집단의 영향 |
| 7 | CHRONIC DISEASE | 만성 질환 | 2=예, 1=아니오 | 만성 질환 보유 여부 |
| 8 | FATIGUE | 피로 | 2=예, 1=아니오 | 만성 피로 증상 |
| 9 | ALLERGY | 알레르기 | 2=예, 1=아니오 | 알레르기 질환 여부 |
| 10 | WHEEZING | 쌕쌕거림 | 2=예, 1=아니오 | 호흡 시 쌕쌕거리는 소리 |
| 11 | ALCOHOL CONSUMING | 음주 | 2=예, 1=아니오 | 음주 습관 여부 |
| 12 | COUGHING | 기침 | 2=예, 1=아니오 | 지속적인 기침 증상 |
| 13 | SHORTNESS OF BREATH | 호흡 곤란 | 2=예, 1=아니오 | 숨이 차는 증상 |
| 14 | SWALLOWING DIFFICULTY | 삼킴 곤란 | 2=예, 1=아니오 | 음식을 삼키기 어려움 |
| 15 | CHEST PAIN | 가슴 통증 | 2=예, 1=아니오 | 가슴 부위의 통증 |

### 데이터 인코딩 규칙

- **성별**: 원본 데이터 'M'/'F' → 모델 입력 1/0
- **증상/습관**: 원본 데이터 1/2 → 모델 입력 그대로 (1=아니오, 2=예)
- **타겟 변수**: 'YES'/'NO' → 1/0 (모델 학습용)

---

## 📖 사용 가이드

### 1. 회원가입 및 로그인

1. 홈 페이지 우측 상단의 **"회원가입"** 버튼 클릭
2. 사용자 이름, 비밀번호 입력 후 가입
3. **"로그인"** 버튼으로 로그인

### 2. 폐암 예측하기

1. 로그인 후 **"예측하기"** 메뉴 클릭
2. 환자의 15개 특성 입력
   - 성별, 나이
   - 증상 (기침, 호흡곤란, 가슴통증 등)
   - 생활습관 (흡연, 음주)
3. **"예측하기"** 버튼 클릭
4. 예측 결과 페이지에서 위험도 확인
   - **높음** (빨강): 70% 이상 → 즉시 전문의 상담 권장
   - **중간** (노랑): 40~70% → 정기적인 검진 권장
   - **낮음** (초록): 40% 미만 → 건강한 생활 습관 유지

### 3. 환자 정보 관리

1. **"환자 목록"** 메뉴에서 등록된 환자 확인
2. 환자명 클릭 → 상세 정보 확인
3. **"수정"** 버튼 → 정보 수정 및 자동 재예측
4. **"삭제"** 버튼 → 환자 정보 삭제 (확인 필요)

### 4. 데이터 시각화

1. **"시각화"** 메뉴 클릭
2. 다양한 차트로 전체 환자 데이터 분석
   - 예측 결과 분포
   - 연령대별 분포
   - 성별 분포
   - 예측 확률 분포

### 5. Q&A 이용

1. **"Q&A"** 메뉴 클릭
2. **"질문하기"** 버튼으로 질문 작성 (로그인 불필요)
3. 관리자 답변 대기
4. 답변 완료 시 Q&A 목록에서 확인

---

## 👨‍💼 관리자 기능

### 슈퍼유저 생성

```bash
python manage.py createsuperuser
```

### Django Admin 접속

```
http://127.0.0.1:8000/admin/
```

### 관리 가능 항목

1. **환자(Patient)**: 전체 환자 정보 조회, 수정, 삭제
2. **공지사항(Notice)**: 공지사항 작성, 수정, 삭제
3. **Q&A**: 질문 조회, 답변 작성, 관리
4. **사용자(User)**: 회원 정보 관리, 권한 설정

### 홈 페이지에서 관리자 기능

- **공지사항 추가**: 홈 페이지 하단의 공지사항 섹션에서 작성
- **공지사항 삭제**: 각 공지사항의 삭제 버튼 클릭
- **Q&A 답변**: Q&A 목록에서 답변 대기 중인 질문 선택 후 답변 작성

---

## 🔄 모델 재학습

데이터를 업데이트하거나 모델을 개선하려면 다음 명령어를 실행합니다:

```bash
python lungcancer/train_model.py
```

### 재학습 프로세스

1. `survey lung cancer.csv` 파일 로드
2. 데이터 전처리 (성별, 타겟 변수 인코딩)
3. 학습/테스트 데이터 분리 (80:20)
4. Random Forest 모델 학습
5. 모델 평가 (정확도, 분류 리포트, 혼동 행렬)
6. 특성 중요도 출력
7. 모델 저장 (`lungcancer/ml_model/`)

### 새 데이터 추가 방법

1. `survey lung cancer.csv` 파일에 새 데이터 추가
2. 데이터 형식 확인:
   - 성별: 'M' / 'F'
   - 증상/습관: 1 (아니오) / 2 (예)
   - 타겟: 'YES' / 'NO'
3. 재학습 스크립트 실행
4. 서버 재시작

---

## ⚠️ 주의사항

### 의료 면책 조항

> ⚠️ **중요**: 이 시스템은 **교육 및 연구 목적**으로 개발되었습니다.
> 
> - 실제 의료 진단을 대체할 수 없습니다.
> - 정확한 진단은 반드시 의료 전문가와 상담해야 합니다.
> - 예측 결과는 참고용일 뿐이며, 의료적 판단의 근거로 사용되어서는 안 됩니다.

### 개발 환경 설정

- `DEBUG = True`: 개발 환경용 설정입니다. 운영 환경에서는 반드시 `False`로 변경하세요.
- `SECRET_KEY`: 운영 환경에서는 환경 변수로 관리하세요.
- `ALLOWED_HOSTS`: 운영 환경에서는 도메인을 추가하세요.

### 데이터베이스

- 현재 SQLite를 사용하고 있습니다. 운영 환경에서는 PostgreSQL, MySQL 등을 권장합니다.
- 정기적으로 데이터베이스 백업을 수행하세요.

### 보안

- 슈퍼유저 비밀번호는 강력하게 설정하세요.
- 환자 데이터는 개인정보이므로 보안에 유의하세요.
- HTTPS를 사용하여 통신을 암호화하세요 (운영 환경).

---

## 📞 개발 정보

### 개발팀

- **기관**: 건양대학교 바이오메디컬공학과
- **프로젝트**: 폐암 조기 진단 지원 시스템
- **연도**: 2025

### 기술 지원

- Django 공식 문서: https://docs.djangoproject.com/
- scikit-learn 문서: https://scikit-learn.org/stable/
- Bootstrap 5 문서: https://getbootstrap.com/docs/5.3/

---

## 📜 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

---

## 📸 스크린샷

### 홈 페이지
- 시스템 개요 및 통계 정보 표시
- 주요 기능으로 바로 이동 가능
- 최신 공지사항 및 Q&A 표시

### 예측 페이지
- 직관적인 폼 인터페이스
- 15개 특성을 카테고리별로 그룹화 (기본 정보, 생활 습관, 증상)
- Bootstrap 기반의 깔끔한 디자인

### 결과 페이지
- 위험도를 시각적으로 표시 (낮음=초록, 중간=노랑, 높음=빨강)
- 진단 결과에 따른 권장 사항 제공
- 예측 확률을 백분율로 표시

### 환자 목록 페이지
- 테이블 형태로 환자 정보 정리
- 예측 결과에 따른 색상 태그
- 빠른 검색 및 정렬 기능

### 시각화 페이지
- 4가지 차트로 데이터 분석
- 통계 정보 요약 카드
- 그래프 이미지는 서버에서 동적 생성

---

## 🔧 트러블슈팅

### 서버 실행 오류

**문제**: `python manage.py runserver` 실행 시 오류

**해결**:
```bash
# 가상환경 활성화 확인
source venv/bin/activate

# 패키지 재설치
pip install -r requirements.txt

# 마이그레이션 재실행
python manage.py migrate
```

### 예측 오류

**문제**: 예측 시 "모델을 찾을 수 없습니다" 오류

**해결**:
```bash
# 모델 재학습
python lungcancer/train_model.py
```

### 시각화 한글 깨짐

**문제**: 차트의 한글이 깨져 보임

**해결**:
- macOS: AppleGothic 폰트 자동 사용 (코드에 이미 적용됨)
- Windows: `plt.rcParams['font.family'] = 'Malgun Gothic'` 설정 필요
- Linux: `plt.rcParams['font.family'] = 'NanumGothic'` 설정 필요

---

## 🎓 학습 자료

이 프로젝트를 통해 다음을 학습할 수 있습니다:

1. **Django 웹 개발**
   - MTV 패턴 (Model-Template-View)
   - 사용자 인증 시스템
   - CRUD 구현
   - Django Admin 활용

2. **머신러닝 통합**
   - scikit-learn 모델 학습
   - 모델 직렬화 (joblib)
   - 웹 애플리케이션에 ML 모델 통합

3. **데이터 시각화**
   - matplotlib/seaborn 차트 생성
   - Base64 인코딩으로 이미지 전송
   - 동적 그래프 생성

4. **UI/UX 디자인**
   - Bootstrap 5 활용
   - 반응형 웹 디자인
   - 사용자 친화적 인터페이스

---

**문의사항이나 버그 리포트는 프로젝트 관리자에게 연락해주세요.**

**© 2025 건양대학교 바이오메디컬공학과. All rights reserved.**
# GitHub Actions 트리거 - Thu Oct 23 14:19:45 KST 2025
# SSH 키 설정 완료 - Thu Oct 23 14:21:11 KST 2025
# SSH 키 설정 완료 - 재배포 테스트 Thu Oct 23 14:24:57 KST 2025
# 새로운 SSH 키 설정 완료 - Thu Oct 23 14:26:38 KST 2025
# 새로운 SSH 키 v2 설정 완료 - Thu Oct 23 14:30:53 KST 2025
# GCP VM 등록된 SSH 키 사용 - Thu Oct 23 14:32:45 KST 2025
# GitHub Actions 재실행 테스트 - Thu Oct 23 14:36:40 KST 2025
# GitHub Actions 재실행 - 새 SSH 키 적용 Thu Oct 23 14:39:27 KST 2025
# GitHub Actions 테스트 - #오후
# GitHub Actions 재실행 - SSH 키 확인 Thu Oct 23 14:45:47 KST 2025
# SSH 키 설정 완료 - 자동 배포 테스트 Thu Oct 23 14:49:28 KST 2025
# GCP 배포 문제 해결 시도 Thu Oct 23 14:51:16 KST 2025
