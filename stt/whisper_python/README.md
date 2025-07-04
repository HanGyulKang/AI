# 🎤 [Speech-to-Text with Faster Whisper](./speech_to_text_final.py)

**개선된 음성 인식 시스템** - 노이즈 제거, 음량 최적화, 오프라인 지원

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [설치 및 설정](#설치-및-설정)
- [사용법](#사용법)
- [기술적 세부사항](#기술적-세부사항)
- [성능 최적화](#성능-최적화)
- [신뢰도 해석](#신뢰도-해석)
- [문제 해결](#문제-해결)

## 🎯 개요

이 프로젝트는 **faster-whisper**를 기반으로 한 고성능 음성 인식 시스템입니다. 노이즈 제거와 음량 최적화 기능을 포함합니다.

### ✨ 핵심 특징

- 🚀 **faster-whisper large-v2 모델** 사용
-  **오프라인 지원** - 모델 캐싱으로 인터넷 없이 실행
- 🎵 **노이즈 제거** - Low-pass filter (3000Hz) 적용
-  **음량 최적화** - 자동 정규화 및 볼륨 증폭

## ️ 주요 기능

### 1. 오디오 전처리 (Audio Preprocessing)

```python
def preprocess_audio(audio):
    # 스테레오 → 모노 변환
    if audio.channels == 2:
        audio = audio.set_channels(1)
    
    # 샘플레이트 16kHz 변환
    if audio.frame_rate != 16000:
        audio = audio.set_frame_rate(16000)
    
    # 오디오 정규화
    audio = normalize(audio)
    
    # Low-pass filter (3000Hz) - 노이즈 제거
    audio = low_pass_filter(audio, 3000)
    
    # 음량 5dB 증가
    audio = audio + 5
```

### 2. 모델 관리 (Model Management)
한 번 다운받은 모델에 대해서는 재다운로드를 받지 않고 캐싱 된 파일을 재사용합니다.

```python
def get_whisper_model():
    # GPU/CPU 자동 감지
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    
    # 오프라인 모드 우선 시도
    try:
        model = WhisperModel("large-v2", local_files_only=True)
    except:
        # 온라인 다운로드 (최초 1회만)
        model = WhisperModel("large-v2", local_files_only=False)
```

##  설치 및 설정

### 1. 의존성 설치

```bash
pip install faster-whisper
pip install pydub
pip install torch
```

### 2. 모델 다운로드 (최초 1회)

```python
from faster_whisper import WhisperModel

# 인터넷 연결 필요 (최초 1회만)
model = WhisperModel("large-v2", device="cpu", compute_type="int8")
```

## 🚀 사용법

### 기본 사용법

```python
from speech_to_text_final import convert_audio_to_text_improved

# 단일 파일 처리
result = convert_audio_to_text_improved("path/to/audio.mp3")
print(result)
```

### 배치 처리

```python
from speech_to_text_final import process_multiple_files

# 여러 파일 처리
file_paths = ["file1.mp3", "file2.wav", "file3.m4a"]
results = process_multiple_files(file_paths)
```

### 메인 함수 실행

```bash
python speech_to_text_final.py
```

##  기술적 세부사항

### 최적화된 Whisper 파라미터

```python
segments, info = model.transcribe(
    audio_path,
    language="ko",
    
    # 정확도 향상
    beam_size=5,           # 빔 서치 크기 증가
    best_of=5,             # 더 많은 후보 검토
    temperature=0.0,        # 결정적 결과 유지
    
    # 컨텍스트 고려
    condition_on_previous_text=True,
    initial_prompt="",
    
    # VAD (Voice Activity Detection)
    vad_filter=True,
    vad_parameters=dict(
        min_silence_duration_ms=1000,  # 1초 무음 허용
        speech_pad_ms=300              # 0.3초 패딩
    ),
    
    # 임계값 조정
    compression_ratio_threshold=2.4,   # 압축 비율 임계값
    no_speech_threshold=0.3,           # 무음 임계값 (0.6 → 0.3)
    
    # 반복 처리
    repetition_penalty=0.8,            # 반복 패널티 완화
    length_penalty=1.0,                # 길이 패널티 유지
    
    # 기타 옵션
    word_timestamps=False,             # 단어별 타임스탬프 비활성화
    suppress_tokens=[-1],              # EOT 토큰 억제
    without_timestamps=False,          # 타임스탬프 유지
    max_initial_timestamp=1.0,         # 초기 타임스탬프 최대값
)
```

### 오디오 전처리 파이프라인

1. **채널 변환**: 스테레오 → 모노 (음성 인식에 최적화)
2. **샘플레이트 변환**: 16kHz (Whisper 모델 표준)
3. **정규화**: 볼륨 레벨 자동 조정
4. **노이즈 제거**: Low-pass filter (3000Hz)
5. **음량 증폭**: +5dB 증가

## ⚡ 성능 최적화

### 1. 모델 재사용

```python
# 싱글톤 패턴으로 모델 재사용
_whisper_model = None
_model_loaded = False

def get_whisper_model():
    global _whisper_model, _model_loaded
    if not _model_loaded:
        # 모델 로딩 로직
        _model_loaded = True
    return _whisper_model
```

### 2. 파일 크기 제한

- **최대 길이**: 30분
- **자동 자르기**: 30분 초과 시 자동으로 잘림

### 3. 임시 파일 관리

```python
# 임시 WAV 파일 자동 정리
temp_wav_path = "/tmp/temp_audio_optimized.wav"
try:
    # 처리 로직
finally:
    if os.path.exists(temp_wav_path):
        os.remove(temp_wav_path)
```

##  신뢰도 해석 가이드

### 신뢰도 점수 범위

| 신뢰도 범위 | 의미 | 권장사항 | 이모지 |
|------------|------|----------|--------|
| -0.1 ~ 0.0 | 매우 높음 | 결과를 신뢰할 수 있음 | ✅ |
| -0.3 ~ -0.1 | 높음 | 대부분 정확함 | ✅ |
| -0.6 ~ -0.3 | 보통 | 검토 권장 | ⚠️ |
| -1.0 ~ -0.6 | 낮음 | 수동 검토 필요 | ❌ |
| -1.0 이하 | 매우 낮음 | 재녹음 또는 다른 방법 고려 |  |

### 신뢰도에 영향을 주는 요소

-  **음성 품질**: 명확한 발음, 적절한 볼륨
-  **녹음 환경**: 배경 노이즈, 에코
- ️ **화자 특성**: 발음, 억양, 속도
- 🎼 **음악 요소**: 반복 구간, 겹치는 음성

