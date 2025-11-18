# LoRa-bam-reconstruction

**Ultra-low SNR LoRa 신호 디노이징 및 재구성**

BAM (Bidirectional Associative Memory) 기반 압축/복원을 통한 LoRa 신호 처리

## Python Version
3.12.10

## 프로젝트 구조

```
Model-experiment-v3/   # BAMv3: Self-supervised (노이즈→노이즈)
Model-experiment-v4/   # BAMv4: Supervised Denoising (노이즈→클린)
Model-experiment-1/    # 초기 실험 (레거시)
Model-experiment-2/    # 초기 실험 (레거시)
utils/                 # LoRa 유틸리티 및 BAM 구현
```

## 실험 비교: v3 vs v4

| 특징 | BAMv3 | BAMv4 |
|------|-------|-------|
| 학습 방식 | Self-supervised | Supervised |
| 입력 | 노이즈 신호 | 노이즈 신호 |
| 타겟 | 노이즈 신호 | **클린 신호** |
| 최적화 | 커스텀 BAM 알고리즘 | PyTorch Adam |
| 클린 타겟 필요 | ❌ 불필요 | ✅ 필요 |
| Ultra-low SNR | ✅ 특화 | ⚠️ Gradient 문제 가능 |
| 이론적 배경 | Robust Feature Learning | Denoising Autoencoder |

### BAMv3 (권장: Ultra-low SNR)
- 노이즈가 신호보다 훨씬 큰 환경 (-30dB ~ -10dB)
- 병목 효과를 통한 자연스러운 디노이징
- 실전 환경 (클린 참조 없음)

### BAMv4 (권장: 일반 SNR)
- 명확한 디노이징 목표
- 빠른 수렴 가능성
- 클린 타겟이 있을 때

## 사용법

### 1. 데이터셋 생성
```bash
cd Model-experiment-v3  # 또는 v4
jupyter notebook generate.ipynb
# GENERATE = True로 설정 후 실행
```

### 2. 학습
```bash
jupyter notebook training.ipynb
# TRAIN = True로 설정 후 실행
```

### 3. 평가
```bash
jupyter notebook main.ipynb
```

## 주요 파라미터

- **SF (Spreading Factor)**: 9
- **BW (Bandwidth)**: 250 kHz
- **fs (Sampling Rate)**: 1 MHz (OSF=4)
- **SNR 범위**: -30 dB ~ 15 dB
- **심볼 개수**: 512 (0-511)

## 성능 평가 지표

1. Spectrogram 유사도
2. Dechirp 후 Code 복원 정확도
3. Ultra-low SNR에서의 디코딩 성공률

## License

MIT License
