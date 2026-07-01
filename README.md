# LoRa-bam-reconstruction

초저 SNR(-15dB 이하 구간 타겟) LoRa 심볼 복원을 BAM(Bidirectional Associative Memory) 계열 모델로 시도하는 실험 저장소.

## 결론 먼저

- 출발점은 기존 디코딩 코드의 de-chirp 구현 오류 — `estimate_symbol(...)`이 `power[:2^sf]`로 앞 bin만 잘라 보던 탓에 **OSF>1일 때 FFT power의 OSF-fold 합산이 누락**되어 있었음. `utils/my_lora_utils.py:estimate_symbol_custom`에서 `power.reshape(osf, num_symbols).sum(axis=0)`로 power를 OSF-fold 합산하도록 수정한 것이 모든 후속 실험의 기준선.
- 초저 SNR 구간에서 baseline(원 IQ 직접 디코딩) 대비 복원율이 의미 있게 개선된 모델은 아직 없음. 목표(초저 SNR에서 baseline을 상회) 미달.
- **출력 collapse(입력 다름 → 출력 동일/상수에 수렴) 관측 모델: v3-ultra, v4.** 평가 시 SNR과 무관하게 BAM 복원 후 심볼 정답률이 0.0~0.5% 구간(512심볼 균일 추측 ≈0.2%)에 머무름.
- v5/v6/basic-bam 계열은 collapse는 아니지만 모든 SNR에서 baseline 대비 net negative 또는 동률.

## 공통 설정

- SF = 9 (심볼 수 = 2^9 = 512)
- 한 심볼당 데이터 = 클린 IQ 1개 × 노이즈 realization N개 (폴더별로 N과 SNR 범위가 다름)
- 학습/평가 SNR 범위는 폴더별로 달리하며 탐색. 타겟 구간은 대략 -15 dB 이하.

## 폴더 구성

```
LoRa-bam-reconstruction/
├── utils/                          # 공용: LoRa 클래스, BAM 구현, 심볼 추정
├── Model-complex/                  # 단층 Complex-Valued BAM (ComplexIQBAM)
├── Model-experiment-basic-bam/     # STFT magnitude(dB) + MultiBAM (self-supervised)
├── Model-experiment-v3-ultra/      # Complex 스펙트로그램 + MultiBAMv3 (Torch 선형)
├── Model-experiment-v4/            # Complex 스펙트로그램 + MultiBAMv4 (tied AE)
├── Model-experiment-v5/            # Complex 스펙트로그램 + MultiBAMv5 (untied + outer residual + Huber)
├── Model-experiment-v6/            # Complex 스펙트로그램 + MultiBAMv6 (Residual FC blocks)
└── simulation_theory/              # 복소수 활성함수(modReLU, zReLU) 시각화
```

### utils/
- `LoRa.py` — LoRa 심볼 생성/AWGN(`LoRa` 클래스) + BAM 계열(`BAM`/`MultiBAM`, `BAMv3`/`MultiBAMv3`, `BAMv3_Huber`, `BAMv4`/`MultiBAMv4`, `MultiBAMv5`, `ResidualFCBlock`/`MultiBAMv6`, `ComplexIQBAM`) 구현.
- `my_lora_utils.py` — `estimate_symbol_custom(a, sf, fs, bw)`: dechirp + FFT + OSF-fold power 합산으로 심볼 추정.
- `simulatiuon.py` — `estimate_symbol_custom` 단독 사본(파일명 오타).

### Model-complex/
- 단층 Complex-Valued BAM(`ComplexIQBAM`). dv/dt·du/dt Euler 동역학 + split-tanh + gain clamp + anchor 구조로 IQ를 직접 입력받아 복원.
- `generate.ipynb`: SF=9, BW=125 kHz, OSF=8, fs=1 MHz. 512심볼 × `NOISY_PER_CLEAN=10` realization, **SNR ~ U[-30, 0] dB (BW 기준)** 으로 noisy/clean IQ 쌍을 사전 저장.
- `training.ipynb`: 위 사전 생성 쌍을 로드해 complex MSE로 학습, SNR 5dB bin으로 복원 MSE와 `estimate_symbol_custom` 기반 심볼 정확도를 집계. 노트북에 저장된 실행 출력이 없어 정량 결과는 현재 미확정.

### Model-experiment-basic-bam/
- 모두 IQ → STFT → BW crop → **magnitude(dB) 또는 magnitude flatten** 도메인에서 BAM을 학습. ISTFT를 거치지 않고 스펙트로그램에서 바로 심볼을 추정하는 파이프라인.
- 공통: SF=9, BW=125 kHz, OSF=8, fs=1 MHz, clean IQ는 `dataset_sf9_bw125k/clean_iq/`에서 로드, 노이즈는 학습 시 on-the-fly 추가.
- `training_basic.ipynb` — "FEBAM"(확장→압축→확장) 깊은 `MultiBAM`(NumPy 선형), clean-only self-supervised. 평가 SNR {0, -5, …, -30}. 현 노트북은 `estimate_from_spectrogram` 미정의로 평가 직전 중단됨.
- `training_2i.ipynb` — 같은 파이프라인을 레이어 차원 2^i 단계로 구성한 `MultiBAM`. 평가 SNR {0, -5, …, -25}. 평가 표가 모든 SNR에서 before/after 모두 0%로 나와 있어 평가 파이프라인 자체가 동작하지 않은 상태.
- `singleLayer.ipynb` — 단층 `MultiBAM`, 학습 SNR randint(-5, +5), 평가 SNR {-30, …, +5}. 모든 SNR에서 baseline 대비 BAM이 동률 또는 낮음(예: -25 dB baseline 51% → BAM 26%).
- `singleLayer_originalBAM.ipynb` — 원 `BAM` 클래스의 `train(X)` self-supervised(X→X), 학습 SNR randint(-25, 0), 평가 SNR {-30, …, +5}. 위와 동일 양상(예: -20 dB baseline 99.8% → BAM 42.4%).

### Model-experiment-v3-ultra/
- Complex 스펙트로그램(real/imag concat flatten, 7936-dim) + `MultiBAMv3` (Torch tensor, identity 활성, target 기반 W 갱신 + weight decay + grad-norm clip). 레이어 7936 → 4096 → 3072 → 2048.
- SF=9, BW=**250 kHz**, OSF=**4**, fs=1 MHz. 학습 SNR randint(-5, +5), 평가 SNR {-30, …, -5}.
- 평가에서 BAM 정답률이 SNR 무관하게 0.0~0.4%에 머물러 **출력 collapse 관측됨** (baseline은 -5 dB에서 100%).

### Model-experiment-v4/
- Complex 스펙트로그램(real/imag concat) + `MultiBAMv4` (PyTorch, tied encoder/decoder W^T, leaky_relu, MSE + Adam, denoising AE).
- SF=9, BW=125 kHz, OSF=8. 학습 SNR U(-7.5, 0), 평가 SNR {-30, …, -5}.
- v3-ultra와 동일하게 모든 SNR에서 BAM 정답률 0.1~0.5%로 **출력 collapse 관측됨**. 단일 심볼 디버깅에서도 복원 신호 peak이 클린 대비 0.2% 수준.

### Model-experiment-v5/
- Complex 스펙트로그램 + `MultiBAMv5` (untied encoder/decoder + outer residual `x + α·δ` + Huber loss + Adam).
- SF=9, BW=125 kHz, OSF=8. 학습 SNR U(-7.5, 0), 평가 SNR {-30, …, -5}.
- collapse는 없음. BAM 정답률은 SNR을 따라 변하나 모든 SNR에서 baseline보다 낮음(예: -20 dB baseline 99.4% vs BAM 74.1%).

### Model-experiment-v6/
- Complex 스펙트로그램 + `MultiBAMv6` (encoder/decoder가 `ResidualFCBlock` 스택, outer residual, `residual_alpha`를 epoch 따라 스케줄링).
- SF=9, BW=125 kHz, OSF=8. 학습 SNR U(-7.5, 0), 평가 SNR {-30, …, -5}.
- collapse는 없음. baseline과 거의 같거나 약간 낮음(-25/-20 dB에서 baseline 대비 각각 -8.1, -12.2 %p).

### simulation_theory/
- LoRa와 무관한 시각화용 노트북 하나. modReLU, zReLU 복소수 활성함수를 복소평면 magnitude/phase로 그리고, 실축/대각 슬라이스를 비교.

## 데이터셋

폴더마다 자체 `generate.ipynb`로 클린 IQ를 생성. 노이즈는 폴더에 따라 (a) generate 단계에서 사전 저장(Model-complex), (b) 학습 시 on-the-fly 추가(나머지) 중 하나로 구분.

- `dataset_sf9_bw125k_osf8_fs1MHz/{clean_iq, noisy_iq}/sym_XXX*.npy` — Model-complex (사전 noisy 포함)
- `dataset_sf9_bw125k/clean_iq/sym_XXX_iq.npy` — basic-bam
- `dataset_v3_sf9_bw250k/clean_iq/sym_XXX_iq.npy` — v3-ultra (BW=250 kHz, OSF=4)
- `dataset_sf9_bw125k/` 또는 동등 경로 — v4/v5/v6 (on-the-fly augmentation)

각 파일은 클린 LoRa 심볼 1개 분량의 complex IQ(`2^sf × OSF` 샘플, complex64).

## 핵심 함수

### `estimate_symbol_custom` (`utils/my_lora_utils.py`)
```python
def estimate_symbol_custom(a, sf, fs, bw):
    # 1. signal_len이 2^sf의 정수배가 아니면 잘라 맞춤
    # 2. osf = signal_len // 2^sf
    # 3. down-chirp 생성 후 dechirp
    # 4. FFT → power = |spectrum|^2
    # 5. osf > 1이면 power.reshape(osf, 2^sf).sum(axis=0) 으로 OSF-fold 합산
    # 6. argmax → symbol index
```

전제: 입력은 LoRa 심볼 1개 분량, 길이는 `2^sf`의 정수배, generate 시점의 sf/fs/bw와 일치해야 함.
