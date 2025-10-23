import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

def train_lung_cancer_model():
    """폐암 예측 머신러닝 모델 학습 및 저장"""
    
    # 데이터 로드
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    data_path = os.path.join(project_dir, 'survey lung cancer.csv')
    
    df = pd.read_csv(data_path)
    
    print("="*50)
    print("폐암 예측 모델 학습 시작")
    print("="*50)
    print(f"데이터 크기: {df.shape}")
    print(f"클래스 분포:\n{df['LUNG_CANCER'].value_counts()}")
    
    # 성별을 숫자로 변환 (M=1, F=0)
    df['GENDER'] = df['GENDER'].map({'M': 1, 'F': 0})
    
    # 타겟 변수를 숫자로 변환 (YES=1, NO=0)
    df['LUNG_CANCER'] = df['LUNG_CANCER'].map({'YES': 1, 'NO': 0})
    
    # 특성과 타겟 분리
    X = df.drop('LUNG_CANCER', axis=1)
    y = df['LUNG_CANCER']
    
    # 특성 이름 저장
    feature_names = X.columns.tolist()
    
    # 학습/테스트 데이터 분리
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 모델 학습 - RandomForest
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # 예측 및 평가
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n모델 학습 완료!")
    print(f"정확도: {accuracy:.4f}")
    print("\n분류 리포트:")
    print(classification_report(y_test, y_pred, target_names=['NO', 'YES']))
    print("\n혼동 행렬:")
    print(confusion_matrix(y_test, y_pred))
    
    # 특성 중요도
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n특성 중요도 (상위 10개):")
    print(feature_importance.head(10))
    
    # 모델 저장
    model_dir = os.path.join(current_dir, 'ml_model')
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, 'lung_cancer_model.pkl')
    feature_path = os.path.join(model_dir, 'feature_names.pkl')
    
    joblib.dump(model, model_path)
    joblib.dump(feature_names, feature_path)
    
    print(f"\n모델 저장 완료: {model_path}")
    print(f"특성 이름 저장 완료: {feature_path}")
    print("="*50)
    
    return model, feature_names, accuracy

if __name__ == '__main__':
    train_lung_cancer_model()

