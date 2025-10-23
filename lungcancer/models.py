from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Patient(models.Model):
    """환자 정보 및 폐암 예측 결과 저장 모델"""
    
    GENDER_CHOICES = [
        (1, '남성'),
        (0, '여성'),
    ]
    
    # CSV 학습데이터는 1=아니오, 2=예 로 코딩됨
    YES_NO_CHOICES = [
        (2, '예'),
        (1, '아니오'),
    ]
    
    # 환자 기본 정보
    gender = models.IntegerField('성별', choices=GENDER_CHOICES)
    age = models.IntegerField('나이')
    
    # 증상 및 생활 습관
    smoking = models.IntegerField('흡연', choices=YES_NO_CHOICES)
    yellow_fingers = models.IntegerField('손가락 변색', choices=YES_NO_CHOICES)
    anxiety = models.IntegerField('불안', choices=YES_NO_CHOICES)
    peer_pressure = models.IntegerField('또래 압박', choices=YES_NO_CHOICES)
    chronic_disease = models.IntegerField('만성 질환', choices=YES_NO_CHOICES)
    fatigue = models.IntegerField('피로', choices=YES_NO_CHOICES)
    allergy = models.IntegerField('알레르기', choices=YES_NO_CHOICES)
    wheezing = models.IntegerField('쌕쌕거림', choices=YES_NO_CHOICES)
    alcohol_consuming = models.IntegerField('음주', choices=YES_NO_CHOICES)
    coughing = models.IntegerField('기침', choices=YES_NO_CHOICES)
    shortness_of_breath = models.IntegerField('호흡 곤란', choices=YES_NO_CHOICES)
    swallowing_difficulty = models.IntegerField('삼킴 곤란', choices=YES_NO_CHOICES)
    chest_pain = models.IntegerField('가슴 통증', choices=YES_NO_CHOICES)
    
    # 예측 결과
    prediction = models.CharField('예측 결과', max_length=10, blank=True, null=True)
    prediction_probability = models.FloatField('예측 확률', blank=True, null=True)
    
    # 메타 정보
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '환자'
        verbose_name_plural = '환자 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        gender_str = '남성' if self.gender == 1 else '여성'
        return f"환자 #{self.id} ({gender_str}, {self.age}세) - {self.prediction or '예측 전'}"
    
    def get_symptoms_dict(self):
        """증상 정보를 딕셔너리로 반환"""
        return {
            'GENDER': self.gender,
            'AGE': self.age,
            'SMOKING': self.smoking,
            'YELLOW_FINGERS': self.yellow_fingers,
            'ANXIETY': self.anxiety,
            'PEER_PRESSURE': self.peer_pressure,
            'CHRONIC DISEASE': self.chronic_disease,
            'FATIGUE ': self.fatigue,
            'ALLERGY ': self.allergy,
            'WHEEZING': self.wheezing,
            'ALCOHOL CONSUMING': self.alcohol_consuming,
            'COUGHING': self.coughing,
            'SHORTNESS OF BREATH': self.shortness_of_breath,
            'SWALLOWING DIFFICULTY': self.swallowing_difficulty,
            'CHEST PAIN': self.chest_pain,
        }


class Notice(models.Model):
    """공지사항 모델"""
    
    title = models.CharField('제목', max_length=200)
    content = models.TextField('내용', blank=True)
    is_important = models.BooleanField('중요 공지', default=False)
    is_active = models.BooleanField('활성화', default=True)
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '공지사항'
        verbose_name_plural = '공지사항 목록'
        ordering = ['-is_important', '-created_at']
    
    def __str__(self):
        return f"[{'중요' if self.is_important else '일반'}] {self.title}"


class QnA(models.Model):
    """QnA 모델"""
    
    question = models.TextField('질문')
    answer = models.TextField('답변', blank=True, null=True)
    category = models.CharField('카테고리', max_length=50, default='일반')
    is_answered = models.BooleanField('답변완료', default=False)
    is_active = models.BooleanField('활성화', default=True)
    created_at = models.DateTimeField('등록일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    # 질문자 정보 (로그인하지 않은 사용자도 질문 가능)
    questioner_name = models.CharField('질문자명', max_length=100, blank=True)
    questioner_email = models.EmailField('질문자 이메일', blank=True)
    
    class Meta:
        verbose_name = 'QnA'
        verbose_name_plural = 'QnA 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        status = "답변완료" if self.is_answered else "답변대기"
        return f"[{status}] {self.question[:50]}..."


class UserProfile(models.Model):
    """사용자 프로필 모델"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField('이름', max_length=30, blank=True)
    last_name = models.CharField('성', max_length=30, blank=True)
    email = models.EmailField('이메일', blank=True)
    phone = models.CharField('전화번호', max_length=20, blank=True)
    created_at = models.DateTimeField('생성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    
    class Meta:
        verbose_name = '사용자 프로필'
        verbose_name_plural = '사용자 프로필 목록'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.first_name} {self.last_name}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """사용자 생성 시 자동으로 프로필 생성"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """사용자 저장 시 프로필도 함께 저장"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
