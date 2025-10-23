from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from .forms import CustomUserCreationForm
from django.http import JsonResponse
from .models import Patient, Notice, QnA
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
    patient_count = Patient.objects.count()
    positive_count = Patient.objects.filter(prediction='YES').count()
    negative_count = Patient.objects.filter(prediction='NO').count()
    
    # 공지사항과 QnA 데이터 가져오기
    notices = Notice.objects.filter(is_active=True)[:5]  # 최신 5개만
    qnas = QnA.objects.filter(is_active=True, is_answered=True)[:5]  # 답변완료된 QnA만
    
    context = {
        'patient_count': patient_count,
        'positive_count': positive_count,
        'negative_count': negative_count,
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
            patient = form.save(commit=False)
            
            # 예측 수행
            features = pd.DataFrame([patient.get_symptoms_dict()])
            features = features[feature_names]  # 특성 순서 맞추기
            
            prediction_proba = model.predict_proba(features)[0]
            prediction = model.predict(features)[0]
            
            patient.prediction = 'YES' if prediction == 1 else 'NO'
            patient.prediction_probability = float(prediction_proba[1])
            patient.save()
            
            messages.success(request, f'예측이 완료되었습니다! (ID: {patient.id})')
            return redirect('lungcancer:result', pk=patient.id)
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
    """환자 목록 페이지"""
    if not request.user.is_authenticated:
        messages.warning(request, '로그인이 필요합니다. 로그인 후 환자 관리 기능을 이용하실 수 있습니다.')
        return redirect('lungcancer:login')
    patients = Patient.objects.all()
    return render(request, 'lungcancer/patient_list.html', {'patients': patients})

def patient_detail(request, pk):
    """환자 상세 정보 페이지"""
    if not request.user.is_authenticated:
        messages.warning(request, '로그인이 필요합니다. 로그인 후 환자 정보를 확인하실 수 있습니다.')
        return redirect('lungcancer:login')
    patient = get_object_or_404(Patient, pk=pk)
    
    probability_percent = patient.prediction_probability * 100 if patient.prediction_probability else 0
    
    context = {
        'patient': patient,
        'probability_percent': round(probability_percent, 2),
    }
    return render(request, 'lungcancer/patient_detail.html', context)

def patient_update(request, pk):
    """환자 정보 수정 페이지"""
    if not request.user.is_authenticated:
        messages.warning(request, '로그인이 필요합니다. 로그인 후 환자 정보를 수정하실 수 있습니다.')
        return redirect('lungcancer:login')
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save(commit=False)
            
            # 재예측 수행
            features = pd.DataFrame([patient.get_symptoms_dict()])
            features = features[feature_names]
            
            prediction_proba = model.predict_proba(features)[0]
            prediction = model.predict(features)[0]
            
            patient.prediction = 'YES' if prediction == 1 else 'NO'
            patient.prediction_probability = float(prediction_proba[1])
            patient.save()
            
            messages.success(request, '환자 정보가 수정되고 재예측이 완료되었습니다.')
            return redirect('lungcancer:patient_detail', pk=patient.id)
    else:
        form = PatientForm(instance=patient)
    
    return render(request, 'lungcancer/patient_update.html', {'form': form, 'patient': patient})

def patient_delete(request, pk):
    """환자 정보 삭제"""
    if not request.user.is_authenticated:
        messages.warning(request, '로그인이 필요합니다. 로그인 후 환자 정보를 삭제하실 수 있습니다.')
        return redirect('lungcancer:login')
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        patient.delete()
        messages.success(request, '환자 정보가 삭제되었습니다.')
        return redirect('lungcancer:patient_list')
    
    return render(request, 'lungcancer/patient_delete.html', {'patient': patient})

def visualization(request):
    """데이터 시각화 페이지"""
    patients = Patient.objects.all()
    
    if not patients.exists():
        return render(request, 'lungcancer/visualization.html', {
            'no_data': True
        })
    
    # 데이터프레임 생성
    data = []
    for p in patients:
        data.append({
            'gender': p.gender,
            'age': p.age,
            'prediction': p.prediction,
            'probability': p.prediction_probability,
        })
    df = pd.DataFrame(data)
    
    # 한글 폰트 설정 (macOS)
    plt.rcParams['font.family'] = 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False
    
    # 1. 예측 결과 분포 (파이 차트)
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    prediction_counts = df['prediction'].value_counts()
    colors = ['#ff6b6b' if idx == 'YES' else '#51cf66' for idx in prediction_counts.index]
    labels = ['폐암 양성' if idx == 'YES' else '폐암 음성' for idx in prediction_counts.index]
    ax1.pie(prediction_counts.values, labels=labels, 
            autopct='%1.1f%%', startangle=90, colors=colors)
    ax1.set_title('폐암 예측 결과 분포', fontsize=16, fontweight='bold')
    
    # 이미지를 base64로 인코딩
    buffer1 = BytesIO()
    plt.savefig(buffer1, format='png', dpi=100, bbox_inches='tight')
    buffer1.seek(0)
    image1_png = buffer1.getvalue()
    buffer1.close()
    image1_base64 = base64.b64encode(image1_png).decode()
    plt.close()
    
    # 2. 연령대별 폐암 예측 분포 (바 차트)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    # 연령을 10단위(20대, 30대, ...)로 그룹화
    df['age_decade'] = (df['age'] // 10) * 10
    # 존재하는 연령대만 자연수 순서대로 정렬
    age_order = sorted(df['age_decade'].unique())
    age_prediction = pd.crosstab(df['age_decade'], df['prediction']).reindex(age_order, fill_value=0)
    # 컬럼 순서를 명시적으로 NO, YES로 고정하여 색상 매핑 안정화
    age_prediction = age_prediction.reindex(columns=['NO', 'YES'], fill_value=0)
    
    # 막대 차트를 중앙 정렬로 그리기
    x_pos = range(len(age_prediction.index))
    width = 0.35
    
    # 음성과 양성 막대를 나란히 그리기
    ax2.bar([x - width/2 for x in x_pos], age_prediction['NO'], width, 
            label='음성', color='#51cf66', alpha=0.8)
    ax2.bar([x + width/2 for x in x_pos], age_prediction['YES'], width, 
            label='양성', color='#ff6b6b', alpha=0.8)
    
    ax2.set_title('연령대별 폐암 예측 분포', fontsize=16, fontweight='bold')
    ax2.set_xlabel('연령대', fontsize=12)
    ax2.set_ylabel('환자 수', fontsize=12)
    ax2.legend(loc='upper left')
    # x축 라벨을 "20대" 형식으로 표시하고 중앙 정렬
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([f"{int(x)}대" for x in age_prediction.index], rotation=0)
    plt.tight_layout()
    
    buffer2 = BytesIO()
    plt.savefig(buffer2, format='png', dpi=100, bbox_inches='tight')
    buffer2.seek(0)
    image2_png = buffer2.getvalue()
    buffer2.close()
    image2_base64 = base64.b64encode(image2_png).decode()
    plt.close()
    
    # 3. 성별에 따른 폐암 예측 분포 (바 차트)
    fig3, ax3 = plt.subplots(figsize=(8, 6))
    df['gender_label'] = df['gender'].map({1: '남성', 0: '여성'})
    gender_prediction = pd.crosstab(df['gender_label'], df['prediction'])
    gender_prediction = gender_prediction.reindex(columns=['NO', 'YES'], fill_value=0)
    
    gender_prediction.plot(kind='bar', ax=ax3, color=['#51cf66', '#ff6b6b'], width=0.6)
    ax3.set_title('성별 폐암 예측 분포', fontsize=16, fontweight='bold')
    ax3.set_xlabel('성별', fontsize=12)
    ax3.set_ylabel('환자 수', fontsize=12)
    ax3.legend(['음성', '양성'], loc='upper right')
    ax3.set_xticklabels(ax3.get_xticklabels(), rotation=0)
    plt.tight_layout()
    
    buffer3 = BytesIO()
    plt.savefig(buffer3, format='png', dpi=100, bbox_inches='tight')
    buffer3.seek(0)
    image3_png = buffer3.getvalue()
    buffer3.close()
    image3_base64 = base64.b64encode(image3_png).decode()
    plt.close()
    
    # 4. 예측 확률 분포 (히스토그램)
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    df_with_prob = df[df['probability'].notna()]
    
    ax4.hist(df_with_prob['probability'], bins=20, color='#339af0', edgecolor='black', alpha=0.7)
    ax4.axvline(x=0.5, color='red', linestyle='--', linewidth=2, label='기준선 (0.5)')
    ax4.set_title('폐암 예측 확률 분포', fontsize=16, fontweight='bold')
    ax4.set_xlabel('예측 확률', fontsize=12)
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
    }
    
    context = {
        'chart1': image1_base64,
        'chart2': image2_base64,
        'chart3': image3_base64,
        'chart4': image4_base64,
        'stats': stats,
        'no_data': False,
    }
    
    return render(request, 'lungcancer/visualization.html', context)

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
    qnas = QnA.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'lungcancer/qna_list.html', {'qnas': qnas})

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
