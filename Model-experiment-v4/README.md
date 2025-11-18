# Model Experiment v4: BAMv4

## 학습 전략
**Supervised Denoising (노이즈 → 클린)**

## 특징
- ✅ 명확한 디노이징 목표
- ✅ PyTorch Adam optimizer 사용
- ✅ 클린 타겟과 직접 비교 학습
- ✅ 표준 Denoising Autoencoder 방식

## 동작 원리
1. 클린 IQ 신호 생성 및 저장
2. Training 시 on-the-fly로 랜덤 SNR (-30~15dB) 노이즈 추가
3. **노이즈 신호**를 입력으로, **클린 신호**를 타겟으로 학습
4. MSE Loss를 통해 클린 신호에 가깝게 복원하도록 학습

## 아키텍처
```
Encoder (노이즈): 4352 → 2048 → 512
Decoder (클린):   512 → 2048 → 4352
```
- Decoder는 Encoder weight의 transpose 사용 (BAM 구조 유지)

## 장점
- 명확한 학습 목표 (클린 복원)
- 이론적으로 잘 정립된 방법론
- 클린 참조가 있을 때 효과적
- 빠른 수렴 가능성

## 단점
- 극한 SNR에서 gradient 문제 가능성
- 클린 타겟 필요

## 사용법
```bash
# 1. 데이터셋 생성
jupyter notebook generate.ipynb
# GENERATE = True로 설정 후 실행

# 2. 학습
jupyter notebook training.ipynb
# TRAIN = True로 설정 후 실행
```

## 평가 기준
- Spectrogram 유사도 (클린 vs 복원)
- Dechirp 후 Code 복원 정확도
- 다양한 SNR에서의 디노이징 성능

