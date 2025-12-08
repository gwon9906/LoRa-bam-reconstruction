import numpy as np

def estimate_symbol_final(a, sf, fs, bw):
    # 1. 기본 설정
    num_symbols = 2 ** sf  # 512
    
    # 2. Dechirp (기존과 동일)
    signal_len = len(a)
    t = np.arange(signal_len) / fs
    f0 = -bw / 2
    symbol_time = num_symbols / bw
    
    # Down Chirp 생성
    phase = 2 * np.pi * (f0 * t + (bw / (2 * symbol_time)) * t**2)
    down_chirp = np.conj(np.exp(1j * phase))
    
    dechirped = a * down_chirp
    spectrum = np.fft.fft(dechirped)
    
    # =======================================================
    # ✅ 핵심 수정: Folding (오버샘플링된 신호 합치기)
    # =======================================================
    # FFT 결과: [0 ~ BW] ... (노이즈) ... [-BW ~ 0]
    # 뒤쪽(음수 주파수)에 있는 신호 에너지를 앞쪽으로 가져와서 합칩니다.
    
    # 앞쪽 512개 (양수 대역)
    pos_freq = spectrum[:num_symbols]
    
    # 뒤쪽 512개 (음수 대역)
    neg_freq = spectrum[-num_symbols:]
    
    # 두 신호를 더합니다 (Coherent Adding)
    # 위상 정렬이 완벽하지 않을 수 있으므로, 안전하게 '파워'를 더하는 것도 방법입니다.
    # 여기서는 성능이 더 좋은 Coherent Sum을 먼저 시도합니다.
    folded_spectrum = pos_freq + neg_freq
    
    # 파워 계산 및 최대값 찾기
    power = np.abs(folded_spectrum) ** 2
    symbol = np.argmax(power)
    peak_power = power[symbol]
    
    return symbol, peak_power

def run_simulation_demo():
    # 설정
    sf = 9
    bw = 125000
    osf = 8
    fs = bw * osf
    num_symbols = 2**sf
    snr_db = -25  # 테스트 목표 SNR
    trials = 1000
    
    print(f"Simulation Start: SF{sf}, SNR {snr_db}dB, Trials {trials}")

    correct_count = 0
    
    # 노이즈 레벨 설정
    sig_power = 1.0
    noise_power = sig_power / (10**(snr_db/10))
    noise_std = np.sqrt(noise_power/2)

    for i in range(trials):
        # 1. 랜덤 심볼 생성 및 변조 (Vectorized)
        target = np.random.randint(0, num_symbols)
        
        # Tx Signal 생성
        symbol_time = num_symbols / bw
        t = np.arange(int(symbol_time * fs)) / fs
        
        # 주파수: -BW/2에서 시작하여 BW만큼 증가 (target만큼 shift)
        # 핵심: (Base + Shift) % BW - BW/2 형태로 랩핑 구현
        slope = bw / symbol_time
        f_inst_raw = (slope * t + target * (bw / num_symbols)) % bw
        f_inst = f_inst_raw - bw/2
        
        # 위상 적분 (Phase Accumulation)
        dt = 1/fs
        phase = 2 * np.pi * np.cumsum(f_inst) * dt
        tx_sig = np.exp(1j * phase)
        
        # 2. 노이즈 추가
        noise = noise_std * (np.random.randn(len(tx_sig)) + 1j * np.random.randn(len(tx_sig)))
        rx_sig = tx_sig + noise
        
        # 3. 복조 (수정된 Folding 함수 사용)
        est_symbol, _ = estimate_symbol_final(rx_sig, sf, fs, bw)
        
        if est_symbol == target:
            correct_count += 1
            
    acc = correct_count / trials * 100
    print(f"Result Accuracy: {acc:.2f}%")

# 위에 정의한 estimate_symbol_final 함수가 있어야 합니다.
run_simulation_demo()