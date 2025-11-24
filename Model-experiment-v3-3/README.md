# Model Experiment v3: BAMv3

## 학습 전략
**Self-supervised Learning (노이즈 → 노이즈)**

## 특징
- ✅ Ultra-low SNR 환경에 특화
- ✅ 클린 타겟 불필요
- ✅ Robust feature learning
- ✅ 다양한 SNR에서 일관된 패턴 학습

## 동작 원리
1. 클린 IQ 신호 생성 및 저장
2. Training 시 on-the-fly로 랜덤 SNR (-30~15dB) 노이즈 추가
3. 노이즈 신호를 입력으로, 같은 노이즈 신호를 타겟으로 학습
4. **병목 효과**를 통해 랜덤 노이즈는 제거되고 신호 패턴만 학습

## 아키텍처
```
Input (노이즈): 4352 → 2048 → 512 (압축)
Output (복원): 512 → 2048 → 4352
```

## 장점
- 노이즈가 신호보다 훨씬 큰 극한 환경에서 유리
- 실전 환경처럼 클린 참조가 없어도 작동
- 512개 심볼의 공통 패턴 학습으로 자연스러운 디노이징

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
- Spectrogram 유사도
- Dechirp 후 Code 복원 정확도
- Ultra-low SNR에서의 디코딩 성공률

