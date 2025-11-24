# Model Experiment v5: BAMv5 - FFT Direct Denoising

## 핵심 혁신
**FFT 기반 + Supervised Denoising + On-the-fly Augmentation**

## 특징
- ✅ **STFT 제거**: 시간축 정보 손실 문제 해결
- ✅ **FFT 기반**: 완벽한 길이 보존 (2048 → 2048)
- ✅ **Clean Target**: 명확한 디노이징 목표
- ✅ **On-the-fly**: 무한한 노이즈 variation
- ✅ **BW Crop**: 차원 감소 (2048 → 512 → 1024)

## 동작 원리
1. 클린 IQ 신호 생성 및 저장
2. Training 시 on-the-fly로 랜덤 SNR (-25~-5dB) 노이즈 추가
3. **FFT → BW Crop → Real/Imag 분리** (시간→주파수 변환)
4. **노이즈 신호**를 입력으로, **클린 신호**를 타겟으로 학습
5. **역FFT**로 완벽한 IQ 복원 (2048 samples)

## 아키텍처
```
Input (Noisy FFT): 1024 (512 complex → BW crop)
    ↓
Encoder: 1024 → 256 → 64  (16x 압축)
    ↓
Decoder: 64 → 256 → 1024
    ↓
Output (Clean FFT): 1024 → iFFT → 2048 IQ
```

## v3, v4와의 차이점

| 항목 | v3 | v4 | **v5** |
|------|----|----|--------|
| **변환** | STFT (lossy) | STFT (lossy) | **FFT (lossless)** |
| **타겟** | Noisy | Clean | **Clean** |
| **길이** | 1920→2048 (손실) | 1920→2048 (손실) | **2048→2048** ✅ |
| **입력 차원** | 7936 | 7936 | **1024** ✅ |
| **압축률** | 3.9x | ? | **16x** ✅ |
| **정보 손실** | 높음 (STFT) | 높음 (STFT) | **낮음** ✅ |

## 장점
- 🎯 **LoRa 특성 활용**: Chirp 신호는 주파수 도메인에서 명확
- 🚀 **메모리 효율**: 1024 << 7936 (7배 감소)
- ⚡ **빠른 학습**: 작은 입력 차원
- 📏 **완벽한 길이 보존**: 2048 → 2048 (resample 불필요)
- 🎨 **명확한 목표**: Clean target으로 디노이징 효과 극대화

## 기대 효과
- Peak power 보존 (65% 손실 → 90%+ 보존)
- Symbol 정확도 향상 (39 → 42)
- 낮은 SNR에서 강력한 디노이징

## 사용법
```bash
# 1. 데이터셋 생성 (v3와 동일)
jupyter notebook generate.ipynb
# GENERATE = True로 설정 후 실행

# 2. 학습 (FFT 기반)
jupyter notebook training.ipynb
# TRAIN = True로 설정 후 실행
```

## 평가 기준
- FFT 복원 정확도
- IQ signal MSE (Clean vs Restored)
- Symbol 디코딩 정확도
- Peak power 보존율

