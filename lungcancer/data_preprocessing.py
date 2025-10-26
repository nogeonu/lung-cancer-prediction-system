"""
폐암 데이터 전처리 및 탐색적 데이터 분석 (EDA)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os

def load_and_explore_data(csv_path):
    """데이터 로드 및 기본 탐색"""
    
    print("="*70)
    print("1. 데이터 로드 및 기본 정보")
    print("="*70)
    
    df = pd.read_csv(csv_path)
    
    print(f"\n📊 데이터 크기: {df.shape[0]}행 × {df.shape[1]}열")
    print(f"\n📋 컬럼 목록:")
    print(df.columns.tolist())
    
    print(f"\n🔍 데이터 타입:")
    print(df.dtypes)
    
    print(f"\n📈 기본 통계:")
    print(df.describe())
    
    print(f"\n🎯 타겟 변수 분포:")
    print(df['LUNG_CANCER'].value_counts())
    print(f"비율: {df['LUNG_CANCER'].value_counts(normalize=True) * 100}")
    
    return df

def check_data_quality(df):
    """데이터 품질 확인 (결측치, 중복, 이상치)"""
    
    print("\n" + "="*70)
    print("2. 데이터 품질 확인")
    print("="*70)
    
    # 결측치 확인
    print("\n❓ 결측치 확인:")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("✅ 결측치 없음!")
    else:
        print(missing[missing > 0])
        print(f"총 결측치: {missing.sum()}개")
    
    # 중복 행 확인
    duplicates = df.duplicated().sum()
    print(f"\n🔄 중복 행: {duplicates}개")
    if duplicates > 0:
        print("⚠️  중복 행 제거 권장")
    else:
        print("✅ 중복 행 없음!")
    
    # 각 컬럼의 고유값 확인
    print("\n🔢 각 컬럼의 고유값 개수:")
    for col in df.columns:
        unique_count = df[col].nunique()
        unique_values = df[col].unique()
        print(f"  {col}: {unique_count}개 → {unique_values[:5]}")
    
    return df

def preprocess_data(df):
    """데이터 전처리"""
    
    print("\n" + "="*70)
    print("3. 데이터 전처리")
    print("="*70)
    
    df_processed = df.copy()
    
    # 1. 중복 제거
    original_size = len(df_processed)
    df_processed = df_processed.drop_duplicates()
    removed_duplicates = original_size - len(df_processed)
    print(f"\n🗑️  중복 행 제거: {removed_duplicates}개")
    
    # 2. 결측치 처리 (있다면)
    if df_processed.isnull().sum().sum() > 0:
        print("\n🔧 결측치 처리 중...")
        # 수치형: 중앙값으로 대체
        numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df_processed[col].isnull().sum() > 0:
                median_val = df_processed[col].median()
                df_processed[col].fillna(median_val, inplace=True)
                print(f"  {col}: 중앙값({median_val})으로 대체")
        
        # 범주형: 최빈값으로 대체
        categorical_cols = df_processed.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df_processed[col].isnull().sum() > 0:
                mode_val = df_processed[col].mode()[0]
                df_processed[col].fillna(mode_val, inplace=True)
                print(f"  {col}: 최빈값({mode_val})으로 대체")
    else:
        print("\n✅ 결측치 없음 - 처리 불필요")
    
    # 3. 범주형 변수 인코딩
    print("\n🔤 범주형 변수 인코딩:")
    
    # 성별 인코딩 (M=1, F=0)
    if 'GENDER' in df_processed.columns:
        df_processed['GENDER'] = df_processed['GENDER'].map({'M': 1, 'F': 0})
        print("  ✓ GENDER: M→1, F→0")
    
    # 타겟 변수 인코딩 (YES=1, NO=0)
    if 'LUNG_CANCER' in df_processed.columns:
        df_processed['LUNG_CANCER'] = df_processed['LUNG_CANCER'].map({'YES': 1, 'NO': 0})
        print("  ✓ LUNG_CANCER: YES→1, NO→0")
    
    # 4. 데이터 타입 확인
    print("\n📝 전처리 후 데이터 타입:")
    print(df_processed.dtypes.value_counts())
    
    print(f"\n✅ 전처리 완료! 최종 데이터 크기: {df_processed.shape}")
    
    return df_processed

def analyze_features(df):
    """특성 분석"""
    
    print("\n" + "="*70)
    print("4. 특성 분석")
    print("="*70)
    
    # 수치형 변수 간 상관관계
    print("\n📊 주요 특성과 타겟 변수 간 상관관계:")
    if 'LUNG_CANCER' in df.columns:
        correlations = df.corr()['LUNG_CANCER'].sort_values(ascending=False)
        print(correlations)
        
        print("\n🔝 타겟과 가장 높은 상관관계를 가진 특성 (상위 5개):")
        top_features = correlations.drop('LUNG_CANCER').head(5)
        for feature, corr in top_features.items():
            print(f"  {feature}: {corr:.4f}")
    
    # 클래스 불균형 확인
    print("\n⚖️  클래스 불균형 분석:")
    if 'LUNG_CANCER' in df.columns:
        class_distribution = df['LUNG_CANCER'].value_counts()
        total = len(df)
        print(f"  클래스 0 (음성): {class_distribution.get(0, 0)}개 ({class_distribution.get(0, 0)/total*100:.1f}%)")
        print(f"  클래스 1 (양성): {class_distribution.get(1, 0)}개 ({class_distribution.get(1, 0)/total*100:.1f}%)")
        
        imbalance_ratio = max(class_distribution) / min(class_distribution)
        print(f"  불균형 비율: {imbalance_ratio:.2f}:1")
        
        if imbalance_ratio > 2:
            print("  ⚠️  클래스 불균형 존재 → class_weight='balanced' 권장")
        else:
            print("  ✅ 클래스 균형 양호")

def split_and_scale_data(df, test_size=0.2, random_state=42):
    """데이터 분리 및 스케일링"""
    
    print("\n" + "="*70)
    print("5. 데이터 분리 및 스케일링")
    print("="*70)
    
    # 특성과 타겟 분리
    X = df.drop('LUNG_CANCER', axis=1)
    y = df['LUNG_CANCER']
    
    print(f"\n📦 특성(X) 크기: {X.shape}")
    print(f"🎯 타겟(y) 크기: {y.shape}")
    
    # 학습/테스트 데이터 분리
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=test_size, 
        random_state=random_state,
        stratify=y  # 클래스 비율 유지
    )
    
    print(f"\n✂️  데이터 분리 완료:")
    print(f"  학습 세트: {X_train.shape[0]}개 ({(1-test_size)*100:.0f}%)")
    print(f"  테스트 세트: {X_test.shape[0]}개 ({test_size*100:.0f}%)")
    
    # 클래스 분포 확인
    print(f"\n학습 세트 클래스 분포:")
    print(f"  음성: {(y_train==0).sum()}개")
    print(f"  양성: {(y_train==1).sum()}개")
    
    print(f"\n테스트 세트 클래스 분포:")
    print(f"  음성: {(y_test==0).sum()}개")
    print(f"  양성: {(y_test==1).sum()}개")
    
    # 스케일링 (선택적 - 트리 기반 모델에는 불필요하지만 참고용)
    print("\n📏 스케일링 (참고용 - Random Forest는 스케일링 불필요):")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("  ✓ StandardScaler 적용 완료")
    print(f"  평균: {X_train_scaled.mean():.6f}")
    print(f"  표준편차: {X_train_scaled.std():.6f}")
    
    return X_train, X_test, y_train, y_test, X.columns.tolist()

def main():
    """전체 전처리 파이프라인 실행"""
    
    # 데이터 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    csv_path = os.path.join(project_dir, 'survey lung cancer.csv')
    
    print("\n" + "🫁 "*20)
    print("폐암 데이터 전처리 및 탐색적 데이터 분석 (EDA)")
    print("🫁 "*20)
    
    # 1. 데이터 로드 및 탐색
    df = load_and_explore_data(csv_path)
    
    # 2. 데이터 품질 확인
    df = check_data_quality(df)
    
    # 3. 데이터 전처리
    df_processed = preprocess_data(df)
    
    # 4. 특성 분석
    analyze_features(df_processed)
    
    # 5. 데이터 분리 및 스케일링
    X_train, X_test, y_train, y_test, feature_names = split_and_scale_data(df_processed)
    
    print("\n" + "="*70)
    print("✅ 전처리 파이프라인 완료!")
    print("="*70)
    print("\n이제 train_model.py를 실행하여 모델을 학습시킬 수 있습니다.")
    print("명령어: python lungcancer/train_model.py")
    
    return df_processed, X_train, X_test, y_train, y_test, feature_names

if __name__ == '__main__':
    main()

