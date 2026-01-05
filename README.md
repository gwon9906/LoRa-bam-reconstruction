# LoRa-bam-reconstruction

**Ultra-low SNR LoRa 신호 디노이징 및 재구성**


---

## 📁 프로젝트 구조

```
LoRa-bam-reconstruction/
├── Model-experiment-v3/          # BAMv3: Self-supervised (노이즈→노이즈) - 구조 이상
├── Model-experiment-v4/          # BAMv4: Supervised Denoising (노이즈→클린) - 구조 이상
├── Model-experiment-v5,6/        # 스킵 커넥션 - 학습 
├── Model-experiment-basic-bam/   # 1/3 기본 BAM 실험 - 최근 실험 - magniutde 
└── utils/                        # LoRa 유틸리티 및 BAM 구현
    ├── LoRa.py                   # LoRa 클래스, MultiBAM 구현
    ├── my_lora_utils.py          # estimate_symbol_custom (Dechirp 기반 심볼 추정)
    └── simulation.py
```

---

## ⚙️ LoRa 파라미터

### 기본 설정

| 파라미터 | v3/v4 | basic-bam | 설명 |
|---------|-------|-----------|------|
| **SF** | 9 | 9 | 심볼 개수 = 2^9 = 512 |
| **BW** | 250 kHz | 125 kHz | 신호 대역폭 |
| **OSF** | 4 | 8 | Oversampling Factor |
| **fs** | 1 MHz | 1 MHz | 샘플링 주파수 (= BW × OSF) |
| **샘플/심볼** | 2048 | 4096 | = 2^SF × OSF |

⚠️ **중요**: 실험별로 BW/OSF가 다름 → 파라미터 일관성 필수

---

## 🗂️ 데이터셋 생성

### generate.ipynb 역할

모든 심볼(0~511)에 대한 **클린 IQ 신호** 생성 및 저장

```python
# generate.ipynb
GENERATE = True  # 반드시 True로 설정

for sym in range(512):
    x_clean = lora.gen_symbol_fs(sym, sf=9, bw=250_000, Fs=1_000_000)
    np.save(f"dataset_*/clean_iq/sym_{sym:03d}_iq.npy", x_clean)
```

### 생성 파일

```
dataset_v3_sf9_bw250k/clean_iq/      # v3
dataset_v4_sf9_bw250k/clean_iq/      # v4
dataset_sf9_bw125k/clean_iq/         # basic-bam
├── sym_000_iq.npy  (complex64, 2048 or 4096 샘플)
├── sym_001_iq.npy
└── ...
```

- **총 512개 파일**
- **노이즈 없는 순수 LoRa 심볼**
- Training 시 on-the-fly로 노이즈 추가

---

---

---

## 🔍  함수

### 1. estimate_symbol_custom
**위치**: `utils/my_lora_utils.py`

**방식**: Dechirp + FFT 기반 심볼 추정

```python
def estimate_symbol_custom(a, sf, fs, bw):
    """
    1. Down-chirp 생성 (주파수 선형 하강)
    2. 입력 신호 × Down-chirp (Dechirp)
    3. FFT → 주파수 스펙트럼
    4. 양수/음수 주파수 폴딩 (OSF 처리)
    5. 최대 파워 위치 = 심볼 번호
    """
```

**필수 조건**:
- 신호 길이 = `2^sf × OSF`
- 파라미터 일관성 (generate와 동일한 sf, fs, bw)
- 다운샘플링 금지


---

## 📚 참고

### 핵심 코드 위치
- **LoRa 클래스**: `utils/LoRa.py` - 심볼 생성, AWGN 추가
- **MultiBAM**: `utils/LoRa.py` - 다층 BAM 구현
- **심볼 추정**: `utils/my_lora_utils.py` - `estimate_symbol_custom`
- **스펙트로그램**: `training_2i.ipynb` - STFT, BW Crop, Flatten