from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from .models import Patient, Notice, QnA, LungRecord, LungResult
from django.db.models import Q
from .forms import PatientForm
import joblib
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

# 모델 로드
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'ml_model', 'lung_cancer_model.pkl')
feature_path = os.path.join(current_dir, 'ml_model', 'feature_names.pkl')

model = joblib.load(model_path)
feature_names = joblib.load(feature_path)

def home(request):
    """홈 페이지"""
    # 로컬 데이터베이스 통계
    patient_count = Patient.objects.count()
    positive_count = Patient.objects.filter(prediction='YES').count()
    negative_count = Patient.objects.filter(prediction='NO').count()
    
    # 외부 데이터베이스 통계 (lung_record, lung_result)
    try:
        # lung_record에서 최근 검사 기록 가져오기
        recent_records = LungRecord.objects.using('heart_db').order_by('-created_at')[:10]
        total_records = LungRecord.objects.using('heart_db').count()
        
        # lung_result에서 결과 통계 가져오기
        total_results = LungResult.objects.using('heart_db').count()
        positive_results = LungResult.objects.using('heart_db').filter(prediction='양성').count()
        negative_results = LungResult.objects.using('heart_db').filter(prediction='음성').count()
        
    except Exception as e:
        # 외부 데이터베이스 연결 실패 시 로컬 데이터만 사용
        recent_records = []
        total_records = 0
        total_results = 0
        positive_results = 0
        negative_results = 0
        print(f"외부 데이터베이스 연결 실패: {e}")
    
    # 공지사항과 QnA 데이터 가져오기
    notices = Notice.objects.filter(is_active=True)[:5]  # 최신 5개만
    qnas = QnA.objects.filter(is_active=True, is_answered=True)[:5]  # 답변완료된 QnA만
    
    context = {
        'patient_count': patient_count,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'recent_records': recent_records,
        'total_records': total_records,
        'total_results': total_results,
        'positive_results': positive_results,
        'negative_results': negative_results,
        'notices': notices,
        'qnas': qnas,
    }
    return render(request, 'lungcancer/home.html', context)

def is_staff_user(user):
    """스태프 권한 확인 함수"""
    return user.is_staff

@login_required
@user_passes_test(is_staff_user)
def add_notice(request):
    """공지사항 추가 (스태프만 가능)"""
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content', '')
        is_important = request.POST.get('is_important') == 'on'
        
        if title:
            Notice.objects.create(
                title=title,
                content=content,
                is_important=is_important
            )
            messages.success(request, '공지사항이 성공적으로 등록되었습니다.')
        else:
            messages.error(request, '제목을 입력해주세요.')
    
    return redirect('lungcancer:home')

@login_required
@user_passes_test(is_staff_user)
def delete_notice(request, notice_id):
    """공지사항 삭제 (스태프만 가능)"""
    try:
        notice = get_object_or_404(Notice, id=notice_id)
        notice.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_protect
def login_view(request):
    """로그인 뷰"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'안녕하세요, {username}님!')
                return redirect('lungcancer:home')
            else:
                messages.error(request, '잘못된 사용자명 또는 비밀번호입니다.')
        else:
            messages.error(request, '입력 정보를 확인해주세요.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    """로그아웃 뷰"""
    logout(request)
    messages.info(request, '로그아웃되었습니다.')
    return redirect('lungcancer:home')

@login_required
def change_password(request):
    """비밀번호 변경 뷰"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 세션 유지
            messages.success(request, '비밀번호가 성공적으로 변경되었습니다.')
            return redirect('lungcancer:home')
        else:
            messages.error(request, '비밀번호 변경에 실패했습니다. 입력 정보를 확인해주세요.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'lungcancer/change_password.html', {'form': form})

def predict(request):
    """폐암 예측 페이지"""
    if not request.user.is_authenticated:
        messages.warning(request, '로그인이 필요합니다. 로그인 후 예측 기능을 이용하실 수 있습니다.')
        return redirect('lungcancer:login')
    
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            try:
                patient = form.save(commit=False)
                
                # 예측 수행
                symptoms_dict = patient.get_symptoms_dict()
                features = pd.DataFrame([symptoms_dict])
                features = features[feature_names]  # 특성 순서 맞추기
                
                prediction_proba = model.predict_proba(features)[0]
                prediction = model.predict(features)[0]
                
                patient.prediction = 'YES' if prediction == 1 else 'NO'
                patient.prediction_probability = float(prediction_proba[1])
                patient.save()
                
                # 외부 데이터베이스에도 저장
                try:
                    # 디버그: 환자 정보 확인
                    print(f"DEBUG - 환자 이름: '{patient.name}'")
                    print(f"DEBUG - 환자 ID: {patient.id}")
                    print(f"DEBUG - 만성질환: {patient.chronic_disease}")
                    print(f"DEBUG - 가슴통증: {patient.chest_pain}")
                    print(f"DEBUG - 또래압박: {patient.peer_pressure}")
                    print(f"DEBUG - 흡연: {patient.smoking}")
                    
                    # lung_record에 저장 (2=예, 1=아니오로 통일)
                    lung_record = LungRecord.objects.using('heart_db').create(
                        gender=str(patient.gender),
                        age=patient.age,
                        smoking=patient.smoking,  # 2=예, 1=아니오 (그대로)
                        yellow_fingers=patient.yellow_fingers,
                        anxiety=patient.anxiety,
                        peer_pressure=patient.peer_pressure,
                        chronic_disease=patient.chronic_disease,
                        fatigue=patient.fatigue,
                        allergy=patient.allergy,
                        wheezing=patient.wheezing,
                        alcohol_consuming=patient.alcohol_consuming,
                        coughing=patient.coughing,
                        shortness_of_breath=patient.shortness_of_breath,
                        swallowing_difficulty=patient.swallowing_difficulty,
                        chest_pain=patient.chest_pain,
                        lung_cancer=1,  # 기본값 (아니오)
                        created_at=patient.created_at,
                    )
                    
                    # lung_result에 저장
                    probability_percent = patient.prediction_probability * 100
                    if probability_percent >= 70:
                        risk_level = 'high'
                        risk_message = '폐암 위험도가 높습니다. 즉시 전문의 상담을 권장합니다.'
                    elif probability_percent >= 40:
                        risk_level = 'medium'
                        risk_message = '폐암 위험도가 중간입니다. 정기적인 검진을 권장합니다.'
                    else:
                        risk_level = 'low'
                        risk_message = '폐암 위험도가 낮습니다. 건강한 생활 습관을 유지하세요.'
                    
                    LungResult.objects.using('heart_db').create(
                        record_id=lung_record.id,
                        name=patient.name if patient.name else f'환자 #{patient.id}',
                        gender=lung_record.gender,
                        age=lung_record.age,
                        prediction='양성' if patient.prediction == 'YES' else '음성',
                        risk_score=patient.prediction_probability * 100,
                        created_at=patient.created_at,
                    )
                    
                    messages.success(request, f'예측이 완료되었습니다! (ID: {patient.id}) - 외부 데이터베이스에도 저장되었습니다.')
                    
                except Exception as e:
                    messages.warning(request, f'예측은 완료되었지만 외부 데이터베이스 저장에 실패했습니다: {str(e)}')
                    messages.success(request, f'예측이 완료되었습니다! (ID: {patient.id})')
                
                return redirect('lungcancer:result', pk=patient.id)
                
            except Exception as e:
                messages.error(request, f'예측 중 오류가 발생했습니다: {str(e)}')
                return render(request, 'lungcancer/predict.html', {'form': form})
        else:
            messages.error(request, '입력 정보를 확인해주세요.')
            return render(request, 'lungcancer/predict.html', {'form': form})
    else:
        form = PatientForm()
    
    return render(request, 'lungcancer/predict.html', {'form': form})                                                                                                                                                                                                               

def result(request, pk):
    """예측 결과 페이지"""
    patient = get_object_or_404(Patient, pk=pk)
    
    # 위험도에 따른 색상 및 메시지
    probability_percent = patient.prediction_probability * 100
    
    if probability_percent >= 70:
        risk_level = '높음'
        risk_color = 'danger'
        risk_message = '폐암 위험도가 높습니다. 즉시 전문의 상담을 권장합니다.'
    elif probability_percent >= 40:
        risk_level = '중간'
        risk_color = 'warning'
        risk_message = '폐암 위험도가 중간입니다. 정기적인 검진을 권장합니다.'
    else:
        risk_level = '낮음'
        risk_color = 'success'
        risk_message = '폐암 위험도가 낮습니다. 건강한 생활 습관을 유지하세요.'
    
    context = {
        'patient': patient,
        'probability_percent': round(probability_percent, 2),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'risk_message': risk_message,
    }
    return render(request, 'lungcancer/result.html', context)

def patient_list(request):
    """환자 목록 페이지 - 외부 데이터베이스 결과만 표시"""
    if not request.user.is_authenticated:
        messages.warning(request, '로그인이 필요합니다. 로그인 후 환자 관리 기능을 이용하실 수 있습니다.')
        return redirect('lungcancer:login')
    
    # 검색어 가져오기
    query = request.GET.get('q', '')
    
    # 외부 데이터베이스 결과만 가져오기
    external_results = []
    db_connected = False
    
    try:
        #external_results = LungResult.objects.using('heart_db').order_by('-created_at')
        results_qs = LungResult.objects.using('heart_db').order_by('-created_at')
        if query:
            results_qs = results_qs.filter(name__icontains=query)
        
        external_results = results_qs
     
        db_connected = True
    except Exception as e:
        print(f"외부 데이터베이스 연결 실패: {e}")
    
    context = {
        'external_results': external_results,
        'db_connected': db_connected,
        'query': query,  # 검색어를 템플릿으로 전달
    }
    return render(request, 'lungcancer/patient_list.html', context)

def patient_delete(request, result_id=None, pk=None):
    """환자 결과 삭제 - LungResult와 연결된 LungRecord 모두 삭제"""
    if not request.user.is_authenticated:
        messages.warning(request, '로그인이 필요합니다.')
        return redirect('lungcancer:login')
    
    # result_id 또는 pk 중 하나를 사용
    target_id = result_id if result_id is not None else pk
    
    try:
        # 외부 데이터베이스에서 삭제
        result = LungResult.objects.using('heart_db').get(result_id=target_id)
        record_id = result.record_id  # 연결된 record_id 저장
        
        # 1. LungResult 삭제
        result.delete()
        
        # 2. 연결된 LungRecord도 삭제 (검사 데이터와 예측 결과 모두 삭제)
        try:
            record = LungRecord.objects.using('heart_db').get(id=record_id)
            record.delete()
            messages.success(request, f'환자 결과 #{target_id}와 검사 기록 #{record_id}가 삭제되었습니다.')
        except LungRecord.DoesNotExist:
            messages.success(request, f'환자 결과 #{target_id}가 삭제되었습니다. (검사 기록은 이미 삭제됨)')
            
    except LungResult.DoesNotExist:
        messages.error(request, '해당 환자 결과를 찾을 수 없습니다.')
    except Exception as e:
        messages.error(request, f'삭제 중 오류가 발생했습니다: {str(e)}')
    
    return redirect('lungcancer:patient_list')

def patient_update(request, result_id=None, pk=None):
    """환자 정보 수정 - LungResult와 LungRecord 모두 수정"""
    if not request.user.is_authenticated:
        messages.warning(request, '로그인이 필요합니다.')
        return redirect('lungcancer:login')
    
    # result_id 또는 pk 중 하나를 사용
    target_id = result_id if result_id is not None else pk
    
    try:
        result = LungResult.objects.using('heart_db').get(result_id=target_id)
        # 해당 결과와 연결된 LungRecord도 가져오기
        try:
            record = LungRecord.objects.using('heart_db').get(id=result.record_id)
        except LungRecord.DoesNotExist:
            record = None
    except LungResult.DoesNotExist:
        messages.error(request, '해당 환자 결과를 찾을 수 없습니다.')
        return redirect('lungcancer:patient_list')
    
    if request.method == 'POST':
        try:
            # LungResult 수정 (예측 결과는 수정하지 않음 - 재예측으로 자동 업데이트됨)
            result.name = request.POST.get('name', result.name)
            result.age = int(request.POST.get('age', result.age))
            result.gender = request.POST.get('gender', result.gender)  # 성별도 업데이트
            # prediction과 risk_score는 재예측으로 자동 업데이트되므로 수정하지 않음
            result.save(using='heart_db')
            
            # LungRecord가 있으면 함께 수정
            if record:
                record.age = int(request.POST.get('age', record.age))
                record.gender = request.POST.get('gender', record.gender)
                
                # Integer 필드들 수정 (드롭다운 값 처리: 1=아니오, 2=예)
                record.smoking = int(request.POST.get('smoking', 1))
                record.yellow_fingers = int(request.POST.get('yellow_fingers', 1))
                record.anxiety = int(request.POST.get('anxiety', 1))
                record.peer_pressure = int(request.POST.get('peer_pressure', 1))
                record.chronic_disease = int(request.POST.get('chronic_disease', 1))
                record.fatigue = int(request.POST.get('fatigue', 1))
                record.allergy = int(request.POST.get('allergy', 1))
                record.wheezing = int(request.POST.get('wheezing', 1))
                record.alcohol_consuming = int(request.POST.get('alcohol_consuming', 1))
                record.coughing = int(request.POST.get('coughing', 1))
                record.shortness_of_breath = int(request.POST.get('shortness_of_breath', 1))
                record.swallowing_difficulty = int(request.POST.get('swallowing_difficulty', 1))
                record.chest_pain = int(request.POST.get('chest_pain', 1))
                # lung_cancer는 예측 결과이므로 수정하지 않음
                
                record.save(using='heart_db')
            
            # 재예측 수행
            try:
                print(f"DEBUG - 재예측 시작: Result ID {target_id}")
                print(f"DEBUG - record 존재: {record is not None}")
                if record:
                    print(f"DEBUG - 가슴통증: {record.chest_pain}, 또래압박: {record.peer_pressure}")
                
                # 수정된 데이터로 재예측 (feature_names와 정확히 일치하도록)
                symptoms_dict = {
                    'GENDER': int(record.gender) if record else int(result.gender),
                    'AGE': int(request.POST.get('age', result.age)),
                    'SMOKING': record.smoking if record else 1,  # 그대로 사용 (2=예, 1=아니오)
                    'YELLOW_FINGERS': record.yellow_fingers if record else 1,
                    'ANXIETY': record.anxiety if record else 1,
                    'PEER_PRESSURE': record.peer_pressure if record else 1,
                    'CHRONIC DISEASE': record.chronic_disease if record else 1,  # 공백 포함
                    'FATIGUE ': record.fatigue if record else 1,  # 뒤에 공백
                    'ALLERGY ': record.allergy if record else 1,  # 뒤에 공백
                    'WHEEZING': record.wheezing if record else 1,
                    'ALCOHOL CONSUMING': record.alcohol_consuming if record else 1,  # 공백 포함
                    'COUGHING': record.coughing if record else 1,
                    'SHORTNESS OF BREATH': record.shortness_of_breath if record else 1,  # 공백 포함
                    'SWALLOWING DIFFICULTY': record.swallowing_difficulty if record else 1,  # 공백 포함
                    'CHEST PAIN': record.chest_pain if record else 1,  # 공백 포함
                    # 'LUNG_CANCER'는 예측 결과이므로 제외
                }
                
                # 예측 수행 (predict 함수와 동일한 로직)
                features = pd.DataFrame([symptoms_dict])
                features = features[feature_names]  # 특성 순서 맞추기
                
                prediction_proba = model.predict_proba(features)[0]
                prediction = model.predict(features)[0]
                
                # 예측 결과 업데이트
                result.prediction = '양성' if prediction == 1 else '음성'
                result.risk_score = round(prediction_proba[1] * 100, 2)
                result.save(using='heart_db')
                
                messages.success(request, f'환자 정보 #{target_id}가 수정되었습니다. 재예측이 완료되었습니다.')
            except Exception as e:
                print(f"재예측 중 오류 발생: {e}")
                messages.warning(request, f'환자 정보는 수정되었지만 재예측 중 오류가 발생했습니다: {str(e)}')
            
            return redirect('lungcancer:patient_list')
        except Exception as e:
            messages.error(request, f'수정 중 오류가 발생했습니다: {str(e)}')
    
    context = {
        'result': result,
        'record': record,
    }
    return render(request, 'lungcancer/patient_update.html', context)

def patient_detail(request, pk=None, result_id=None):
    """환자 상세 정보 페이지 - 외부 데이터베이스 결과"""
    
    print(f"DEBUG - patient_detail 호출됨: pk={pk}, result_id={result_id}")
    
    if not request.user.is_authenticated:
        messages.warning(request, '로그인이 필요합니다. 로그인 후 환자 정보를 확인하실 수 있습니다.')
        return redirect('lungcancer:login')
    
    # pk 또는 result_id 중 하나를 사용
    target_id = result_id if result_id is not None else pk
    print(f"DEBUG - target_id: {target_id}")
    
    try:
        print(f"DEBUG - LungResult 조회 시작: result_id={target_id}")
        # 외부 데이터베이스에서 결과 조회
        result = LungResult.objects.using('heart_db').get(result_id=target_id)
        print(f"DEBUG - LungResult 조회 성공: {result.name}")
        
        # 해당 결과와 연결된 LungRecord도 가져오기
        try:
            print(f"DEBUG - LungRecord 조회 시작: record_id={result.record_id}")
            record = LungRecord.objects.using('heart_db').get(id=result.record_id)
            print(f"DEBUG - LungRecord 조회 성공")
        except LungRecord.DoesNotExist:
            print(f"DEBUG - LungRecord 없음")
            record = None
        
        # 위험도 퍼센트 계산
        risk_percent = float(result.risk_score) if result.risk_score else 0
        print(f"DEBUG - 위험도 계산: {risk_percent}")
        
        context = {
            'result': result,
            'record': record,
            'risk_percent': round(risk_percent, 2),
        }
        print(f"DEBUG - 템플릿 렌더링 시작")
        return render(request, 'lungcancer/patient_detail.html', context)
        
    except LungResult.DoesNotExist:
        messages.error(request, '해당 환자 결과를 찾을 수 없습니다.')
        return redirect('lungcancer:patient_list')
    except Exception as e:
        messages.error(request, f'환자 정보를 불러오는 중 오류가 발생했습니다: {str(e)}')
        return redirect('lungcancer:patient_list')



def visualization(request):
    """데이터 시각화 페이지 - 외부 데이터베이스만 사용"""
    # 외부 데이터베이스에서 데이터 가져오기
    external_records = []
    external_results = []
    db_status = {'external_connected': False, 'external_count': 0}
    
    try:
        external_records = LungRecord.objects.using('heart_db').all()
        external_results = LungResult.objects.using('heart_db').all()
        db_status['external_connected'] = True
        db_status['external_count'] = external_results.count()
    except Exception as e:
        print(f"외부 데이터베이스 연결 실패: {e}")
    
    # 외부 데이터만 사용
    all_data = []
    
    # 외부 데이터 추가 (LungResult에서)
    for result in external_results:
        all_data.append({
            'name': result.name,
            'gender': result.gender,
            'age': result.age,
            'prediction': 'YES' if result.prediction == '양성' else 'NO',
            'probability': float(result.risk_score) / 100,
            'risk_level': 'unknown',
            'created_at': result.created_at,
            'source': 'external'
        })
    
    if not all_data:
        return render(request, 'lungcancer/visualization.html', {
            'no_data': True
        })
    
    # 데이터프레임 생성
    df = pd.DataFrame(all_data)
    
    # 한글 폰트 설정 (macOS)
    plt.rcParams['font.family'] = 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 1. 예측 결과 분포 (파이 차트)
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    prediction_counts = df['prediction'].value_counts()
    
    if len(prediction_counts) > 0:
        colors = ['#ff6b6b' if idx == 'YES' else '#51cf66' for idx in prediction_counts.index]
        labels = ['폐암 양성' if idx == 'YES' else '폐암 음성' for idx in prediction_counts.index]
        ax1.pie(prediction_counts.values, labels=labels, 
                autopct='%1.1f%%', startangle=90, colors=colors)
    else:
        # 데이터가 없을 때 빈 차트 표시
        ax1.text(0.5, 0.5, '데이터가 없습니다', ha='center', va='center', 
                transform=ax1.transAxes, fontsize=14)
    
    ax1.set_title('폐암 예측 결과 분포', fontsize=16, fontweight='bold')
    
    # 이미지를 base64로 인코딩
    buffer1 = BytesIO()
    plt.savefig(buffer1, format='png', dpi=100, bbox_inches='tight')
    buffer1.seek(0)
    image1_png = buffer1.getvalue()
    buffer1.close()
    image1_base64 = base64.b64encode(image1_png).decode()
    plt.close()
    
    # 2. 성별 폐암 예측 분포 (바 차트)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    
    # 성별 데이터 정리 (1=남성, 0=여성 또는 '1'='남성', '0'='여성')
    df['gender_label'] = df['gender'].apply(lambda x: '남성' if x == 1 or x == '1' else '여성')
    gender_prediction = pd.crosstab(df['gender_label'], df['prediction'])
    
    # 컬럼 순서를 명시적으로 NO, YES로 고정
    gender_prediction = gender_prediction.reindex(columns=['NO', 'YES'], fill_value=0)
    
    # 막대 차트 그리기
    x_pos = range(len(gender_prediction.index))
    width = 0.35
    
    # 음성과 양성 막대를 나란히 그리기
    bars1 = ax2.bar([x - width/2 for x in x_pos], gender_prediction['NO'], width, 
            label='음성', color='#51cf66', alpha=0.8)
    bars2 = ax2.bar([x + width/2 for x in x_pos], gender_prediction['YES'], width, 
            label='양성', color='#ff6b6b', alpha=0.8)
    
    # 막대 위에 값 표시
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        
        if height1 > 0:
            ax2.text(bar1.get_x() + bar1.get_width()/2., height1 + 0.05,
                    f'{int(height1)}', ha='center', va='bottom', fontweight='bold')
        if height2 > 0:
            ax2.text(bar2.get_x() + bar2.get_width()/2., height2 + 0.05,
                    f'{int(height2)}', ha='center', va='bottom', fontweight='bold')
    
    ax2.set_title('성별 폐암 예측 분포', fontsize=16, fontweight='bold')
    ax2.set_xlabel('성별', fontsize=12)
    ax2.set_ylabel('환자 수', fontsize=12)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(gender_prediction.index)
    ax2.legend(loc='upper right')
    plt.tight_layout()
    
    buffer2 = BytesIO()
    plt.savefig(buffer2, format='png', dpi=100, bbox_inches='tight')
    buffer2.seek(0)
    image2_png = buffer2.getvalue()
    buffer2.close()
    image2_base64 = base64.b64encode(image2_png).decode()
    plt.close()
    
    # 3. 연령대별 폐암 예측 분포 (바 차트)
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    
    # 연령을 10단위(20대, 30대, ...)로 그룹화
    df['age_decade'] = (df['age'] // 10) * 10
    age_prediction = pd.crosstab(df['age_decade'], df['prediction'])
    age_prediction = age_prediction.reindex(columns=['NO', 'YES'], fill_value=0)
    
    # 막대 차트 그리기
    x_pos = range(len(age_prediction.index))
    width = 0.35
    
    bars3 = ax3.bar([x - width/2 for x in x_pos], age_prediction['NO'], width, 
            label='음성', color='#51cf66', alpha=0.8)
    bars4 = ax3.bar([x + width/2 for x in x_pos], age_prediction['YES'], width, 
            label='양성', color='#ff6b6b', alpha=0.8)
    
    ax3.set_title('연령대별 폐암 예측 분포', fontsize=16, fontweight='bold')
    ax3.set_xlabel('연령대', fontsize=12)
    ax3.set_ylabel('환자 수', fontsize=12)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels([f"{int(x)}대" for x in age_prediction.index])
    ax3.legend(loc='upper right')
    plt.tight_layout()
    
    buffer3 = BytesIO()
    plt.savefig(buffer3, format='png', dpi=100, bbox_inches='tight')
    buffer3.seek(0)
    image3_png = buffer3.getvalue()
    buffer3.close()
    image3_base64 = base64.b64encode(image3_png).decode()
    plt.close()

    
    # 4. 위험도 분포 (히스토그램)
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    
    # 위험도 데이터 정리 (probability를 퍼센트로 변환)
    risk_scores = df['probability'] * 100
    
    ax4.hist(risk_scores, bins=20, color='#339af0', edgecolor='black', alpha=0.7)
    ax4.axvline(x=50, color='red', linestyle='--', linewidth=2, label='기준선 (50%)')
    ax4.set_title('폐암 위험도 분포', fontsize=16, fontweight='bold')
    ax4.set_xlabel('위험도 (%)', fontsize=12)
    ax4.set_ylabel('환자 수', fontsize=12)
    ax4.legend()
    plt.tight_layout()
    
    buffer4 = BytesIO()
    plt.savefig(buffer4, format='png', dpi=100, bbox_inches='tight')
    buffer4.seek(0)
    image4_png = buffer4.getvalue()
    buffer4.close()
    image4_base64 = base64.b64encode(image4_png).decode()
    plt.close()
    
    # 통계 정보
    stats = {
        'total_patients': len(df),
        'positive_patients': len(df[df['prediction'] == 'YES']),
        'negative_patients': len(df[df['prediction'] == 'NO']),
        'avg_age': round(df['age'].mean(), 1),
        'male_count': len(df[df['gender'] == 1]),
        'female_count': len(df[df['gender'] == 0]),
        'external_data_count': len([d for d in all_data if 'source' not in d]),
        'local_data_count': len([d for d in all_data if d.get('source') == 'local']),
    }
    
    # 외부 데이터베이스 연결 상태
    db_status = {
        'external_connected': len(external_results) > 0,
        'external_count': len(external_results),
    }
    
    # 통계 정보 계산
    positive_count = len([d for d in all_data if d['prediction'] == 'YES'])
    negative_count = len([d for d in all_data if d['prediction'] == 'NO'])
    avg_age = df['age'].mean() if len(df) > 0 else 0
    
    # 성별 통계 계산 - 차트와 정확히 동일한 방식으로 계산
    # 차트에서 사용하는 gender_label 로직과 동일하게 처리
    male_count = 0
    female_count = 0
    
    for d in all_data:
        gender = d['gender']
        
        # 차트의 gender_label 로직과 정확히 동일: '남성' if x == 1 or x == '1' else '여성'
        if gender == 1 or gender == '1':
            male_count += 1
        else:  # 0, '0' 또는 다른 모든 값은 여성으로 처리
            female_count += 1
    
    # 디버그 출력
    
    stats = {
        'total_patients': len(external_results),
        'positive_patients': positive_count,
        'negative_patients': negative_count,
        'positive_count': positive_count,  # 템플릿 호환성을 위해 추가
        'negative_count': negative_count,  # 템플릿 호환성을 위해 추가
        'avg_age': round(avg_age, 1),
        'male_count': male_count,  # 남성 환자 수
        'female_count': female_count,  # 여성 환자 수
        'external_records_count': len(external_records),
        'external_results_count': len(external_results),
        'total_data': len(all_data),
    }
    
    context = {
        'chart1': image1_base64,
        'chart2': image2_base64,
        'chart3': image3_base64,
        'chart4': image4_base64,
        'stats': stats,
        'db_status': db_status,
        'external_records': external_records[:10],  # 최근 10개만 표시
        'external_results': external_results[:10],  # 최근 10개만 표시
        'no_data': False,
    }
    
    return render(request, 'lungcancer/visualization.html', context)

@csrf_protect
def signup_view(request):
    """회원가입 뷰"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'회원가입이 완료되었습니다! 환영합니다, {user.first_name} {user.last_name}님!')
            return redirect('lungcancer:home')
        else:
            messages.error(request, '회원가입에 실패했습니다. 입력 정보를 확인해주세요.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

def qna_list(request):
    """QnA 목록 페이지"""
    category_id = request.GET.get('category')
    categories = QnA.objects.values_list('category', flat=True).order_by('category').distinct() # 카테고리 목록 추출
    
    if category_id:
        qnas = QnA.objects.filter(category=category_id, is_active=True).order_by('-created_at')
    else:
        qnas = QnA.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'lungcancer/qna_list.html', {'qnas': qnas, 'categories': categories, 'selected_category': category_id})

def qna_ask(request):
    """질문 작성 페이지 (로그인 불필요)"""
    if request.method == 'POST':
        question = request.POST.get('question')
        category = request.POST.get('category', '일반')
        questioner_name = request.POST.get('questioner_name', '')
        questioner_email = request.POST.get('questioner_email', '')
        
        if question:
            QnA.objects.create(
                question=question,
                category=category,
                questioner_name=questioner_name,
                questioner_email=questioner_email
            )
            messages.success(request, '질문이 성공적으로 등록되었습니다. 답변을 기다려주세요.')
            return redirect('lungcancer:qna_list')
        else:
            messages.error(request, '질문을 입력해주세요.')
    
    return render(request, 'lungcancer/qna_ask.html')

@login_required
@user_passes_test(is_staff_user)
def qna_answer(request, pk):
    """답변 작성 페이지 (관리자만)"""
    qna = get_object_or_404(QnA, pk=pk)
    
    if request.method == 'POST':
        answer = request.POST.get('answer')
        if answer:
            qna.answer = answer
            qna.is_answered = True
            qna.save()
            messages.success(request, '답변이 성공적으로 등록되었습니다.')
            return redirect('lungcancer:qna_list')
        else:
            messages.error(request, '답변을 입력해주세요.')
    
    return render(request, 'lungcancer/qna_answer.html', {'qna': qna})
