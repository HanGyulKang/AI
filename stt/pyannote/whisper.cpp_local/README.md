# Whisper.cpp 한국어 STT 설정 가이드

## 🔧 목차
- [Whisper.cpp 한국어 STT 설정 가이드](#whispercpp-한국어-stt-설정-가이드)
  - [🔧 목차](#-목차)
  - [개요](#개요)
  - [사전 요구사항](#사전-요구사항)
  - [설치 및 설정](#설치-및-설정)
    - [1. 저장소 클론](#1-저장소-클론)
    - [2. 한국어 모델 변환](#2-한국어-모델-변환)
    - [3. 빌드](#3-빌드)
  - [모델 지원](#모델-지원)
    - [기본 지원 모델](#기본-지원-모델)
    - [GGML 확장 모델](#ggml-확장-모델)
    - [모델 생성](#모델-생성)
  - [빌드 옵션](#빌드-옵션)
    - [Makefile 설정](#makefile-설정)
    - [빌드 명령어](#빌드-명령어)
  - [사용법](#사용법)
    - [기본 사용법](#기본-사용법)
    - [예시](#예시)
  - [주의사항](#주의사항)
    - [중요 제한사항](#중요-제한사항)
    - [권장사항](#권장사항)

## 개요

이 가이드는 한국어 음성 인식(Speech-to-Text)을 위해 Whisper.cpp를 설정하는 방법을 설명합니다. 오프라인 환경에서도 작동하는 로컬 STT 시스템을 구축할 수 있습니다.

## 사전 요구사항

- **Git LFS** 한국어 파인튜닝 모델 다운로드 시 설치 필수
- **Make** (`brew install make`)
- **CMake** (`brew install cmake`)
- **CUDA Toolkit** (GPU 사용 시)

## 설치 및 설정

### 1. 저장소 클론

다음 세 개의 저장소를 동일한 폴더에 클론합니다:

```bash
# Whisper.cpp (C++ 구현체)
git clone git@github.com:ggerganov/whisper.cpp.git

# OpenAI Whisper (Python 구현체)
git clone https://github.com/openai/whisper

# 한국어 Fine-tuning 모델
git clone https://huggingface.co/seastar105/whisper-medium-ko-zeroth
```

### 2. 한국어 모델 변환

~~굳이 한국어 Fine-tuning 모델을 사용할 생각이 없다면 해당 부분은 건너뛰어도 됨~~
Fine-tuning된 한국어 모델을 GGML 형식으로 변환합니다:

```bash
python3 ./whisper.cpp/models/convert-h5-to-ggml.py ./whisper-medium-ko-zeroth ./whisper .
```

변환 후 생성된 `ggml-model.bin` 파일을 `whisper.cpp/models/` 폴더로 이동합니다.

### 3. 빌드

Whisper.cpp 폴더에서 빌드를 실행합니다:

```bash
cd whisper.cpp
make
```

빌드가 완료되면 `build/bin` 이하에 `whisper-cli` 실행 파일이 생성됩니다.
* `main`으로 실행하는건 버전 올라가면서 사라짐

## 모델 지원

### 기본 지원 모델
```
tiny.en, tiny, base.en, base, small.en, small
medium.en, medium, large-v1, large-v2, large-v3, large-v3-turbo
```

### GGML 확장 모델
```
tiny-q5_1, tiny.en-q5_1, tiny-q8_0
base-q5_1, base.en-q5_1, base-q8_0
small.en-tdrz, small-q5_1, small.en-q5_1, small-q8_0
medium-q5_0, medium.en-q5_0, medium-q8_0
large-v2-q5_0, large-v2-q8_0
large-v3-q5_0, large-v3-turbo-q5_0, large-v3-turbo-q8_0
```

### 모델 생성

추가 모델이 필요한 경우:

```bash
make {model-name}
```

모델 다운로드 경로:

```bash
/models/{model-name}.bin
```

## 빌드 옵션

### Makefile 설정

`Makefile`에 다음 타겟들을 추가하여 다양한 빌드 옵션을 사용할 수 있습니다:

```makefile
.PHONY: build
build:
	cmake -B build $(CMAKE_ARGS)
	cmake --build build --config Release

# CUDA 빌드를 위한 별도 타겟
.PHONY: build-cuda
build-cuda:
	cmake -B build -DGGML_CUDA=1 -DCMAKE_CUDA_ARCHITECTURES="75;86;89"
	cmake --build build --config Release

# Metal 빌드를 위한 별도 타겟 (Apple Silicon용)
.PHONY: build-metal
build-metal:
	cmake -B build -DGGML_METAL=1
	cmake --build build --config Release

# 스마트 빌드 (시스템 자동 감지)
.PHONY: build-smart
build-smart:
	@if command -v nvidia-smi >/dev/null 2>&1; then \
		echo "NVIDIA GPU detected, building with CUDA..."; \
		cmake -B build -DGGML_CUDA=1 -DCMAKE_CUDA_ARCHITECTURES="75;86;89"; \
	elif uname -m | grep -q "arm64"; then \
		echo "Apple Silicon detected, building with Metal..."; \
		cmake -B build -DGGML_METAL=1; \
	else \
		echo "Building with CPU only..."; \
		cmake -B build; \
	fi
	cmake --build build --config Release
```

### 빌드 명령어

```bash
make build-cuda   # CUDA 빌드 (NVIDIA GPU)
make build-metal  # Metal 빌드 (Apple Silicon)
make build-smart  # 권장: 시스템 자동 감지
```

## 사용법

### 기본 사용법

```bash
./whisper-cli -l ko -m models/{model-name}.bin -f {path}/{audio-file-name}.{extension}
```

### 예시

```bash
# 한국어 음성 파일 변환
./whisper-cli -l ko -m models/ggml-model.bin -f audio/sample.wav

# 다른 모델 사용
./whisper-cli -l ko -m models/large-v2.bin -f audio/sample.mp3
```

## 주의사항

### 중요 제한사항

1. **하드웨어 의존성**: Whisper.cpp는 빌드 시 로컬 PC 하드웨어 정보를 기반으로 빌드됩니다. 정적 빌드(`-DBUILD_SHARED_LIBS=OFF`)를 하더라도 다른 PC로 이동 시 동작하지 않을 수 있습니다.

2. **플랫폼별 제한**:
   - **macOS**: 정적 빌드 후에도 다른 Mac으로 전송 시 실행 불가
   - **Windows**: 정적 빌드 후 Windows 초기화 시 정상 작동 확인됨

3. **모델 성능**: 한국어 변환의 경우 `large-v3`보다 `large-v2`가 더 좋은 성능을 보입니다.

4. **화자 분리**: `tdrz` 접미사가 붙은 모델들은 화자 분리 기능을 제공하지만 영문만 지원합니다.

5. **CUDA 아키텍처**: GPU 아키텍처는 사용하는 GPU에 맞게 설정해야 합니다:
   - RTX 20 시리즈: "75"
   - RTX 30/40 시리즈: "86"
   - 최신 GPU: "89"

### 권장사항

- 오프라인 환경 배포 시: Windows 환경에서 정적 빌드 후 배포
- 한국어 인식: `large-v2` 모델 혹은 양자화 모델 `large-v2-q8_0` 추천
- GPU 가속: CUDA Toolkit 설치 후 `make build-cuda` 사용

---

**참고**: 이 설정은 내부 보안이 중요한 오프라인 환경에서 STT 시스템을 구축하기 위한 테스트 결과를 바탕으로 작성되었습니다. 