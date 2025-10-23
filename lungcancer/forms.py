from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Patient, UserProfile

class PatientForm(forms.ModelForm):
    """환자 정보 입력 폼"""
    
    class Meta:
        model = Patient
        fields = [
            'gender', 'age', 'smoking', 'yellow_fingers', 'anxiety',
            'peer_pressure', 'chronic_disease', 'fatigue', 'allergy',
            'wheezing', 'alcohol_consuming', 'coughing', 
            'shortness_of_breath', 'swallowing_difficulty', 'chest_pain'
        ]
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '120'}),
            'smoking': forms.Select(attrs={'class': 'form-control'}),
            'yellow_fingers': forms.Select(attrs={'class': 'form-control'}),
            'anxiety': forms.Select(attrs={'class': 'form-control'}),
            'peer_pressure': forms.Select(attrs={'class': 'form-control'}),
            'chronic_disease': forms.Select(attrs={'class': 'form-control'}),
            'fatigue': forms.Select(attrs={'class': 'form-control'}),
            'allergy': forms.Select(attrs={'class': 'form-control'}),
            'wheezing': forms.Select(attrs={'class': 'form-control'}),
            'alcohol_consuming': forms.Select(attrs={'class': 'form-control'}),
            'coughing': forms.Select(attrs={'class': 'form-control'}),
            'shortness_of_breath': forms.Select(attrs={'class': 'form-control'}),
            'swallowing_difficulty': forms.Select(attrs={'class': 'form-control'}),
            'chest_pain': forms.Select(attrs={'class': 'form-control'}),
        }


class CustomUserCreationForm(UserCreationForm):
    """커스텀 회원가입 폼"""
    email = forms.EmailField(
        label='이메일',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '이메일을 입력하세요'})
    )
    first_name = forms.CharField(
        label='이름',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '이름을 입력하세요'})
    )
    last_name = forms.CharField(
        label='성',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '성을 입력하세요'})
    )
    phone = forms.CharField(
        label='전화번호',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '전화번호를 입력하세요 (선택사항)'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '사용자명을 입력하세요'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '비밀번호를 입력하세요'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '비밀번호를 다시 입력하세요'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # 프로필 생성
            profile = user.profile
            profile.email = self.cleaned_data['email']
            profile.first_name = self.cleaned_data['first_name']
            profile.last_name = self.cleaned_data['last_name']
            profile.phone = self.cleaned_data.get('phone', '')
            profile.save()
        
        return user

