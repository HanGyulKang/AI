# whisper.cpp (한국어 번역)

![whisper.cpp](https://user-images.githubusercontent.com/1991296/235238348-05d0f6a4-da44-4900-a1de-d0707e75b763.jpeg)

[![Actions Status](https://github.com/ggml-org/whisper.cpp/workflows/CI/badge.svg)](https://github.com/ggml-org/whisper.cpp/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Conan Center](https://shields.io/conan/v/whisper-cpp)](https://conan.io/center/whisper-cpp)
[![npm](https://img.shields.io/npm/v/whisper.cpp.svg)](https://www.npmjs.com/package/whisper.cpp/)

안정 버전: [v1.7.6](https://github.com/ggml-org/whisper.cpp/releases/tag/v1.7.6) / [로드맵](https://github.com/orgs/ggml-org/projects/4/)

OpenAI의 Whisper 자동 음성 인식(ASR) 모델의 고성능 추론:

- 순수 C/C++ 구현, 외부 의존성 없음
- Apple Silicon 완벽 지원 - ARM NEON, Accelerate 프레임워크, Metal, [Core ML](#core-ml-support) 최적화
- x86 아키텍처용 AVX 명령어 지원
- [POWER 아키텍처용 VSX 명령어 지원](#power-vsx-intrinsics)
- 혼합 F16 / F32 정밀도
- [정수 양자화 지원](#quantization)
- 런타임 메모리 할당 없음
- [Vulkan 지원](#vulkan-gpu-support)
- CPU 전용 추론 지원
- [NVIDIA GPU를 위한 효율적 GPU 지원](#nvidia-gpu-support)
- [OpenVINO 지원](#openvino-support)
- [Ascend NPU 지원](#ascend-npu-support)
- [Moore Threads GPU 지원](#moore-threads-gpu-support)
- [C 스타일 API](https://github.com/ggml-org/whisper.cpp/blob/master/include/whisper.h)
- [음성 활동 감지(VAD)](#voice-activity-detection-vad)

지원 플랫폼:

- [x] Mac OS (Intel 및 Arm)
- [x] [iOS](examples/whisper.objc)
- [x] [Android](examples/whisper.android)
- [x] [Java](bindings/java/README.md)
- [x] Linux / [FreeBSD](https://github.com/ggml-org/whisper.cpp/issues/56#issuecomment-1350920264)
- [x] [WebAssembly](examples/whisper.wasm)
- [x] Windows ([MSVC](https://github.com/ggml-org/whisper.cpp/blob/master/.github/workflows/build.yml#L117-L144), [MinGW](https://github.com/ggml-org/whisper.cpp/issues/168))
- [x] [Raspberry Pi](https://github.com/ggml-org/whisper.cpp/discussions/166)
- [x] [Docker](https://github.com/ggml-org/whisper.cpp/pkgs/container/whisper.cpp)

모델의 모든 상위 구현은 [whisper.h](include/whisper.h)와 [whisper.cpp](src/whisper.cpp)에 포함되어 있습니다. 나머지 코드는 [`ggml`](https://github.com/ggml-org/ggml) 머신러닝 라이브러리의 일부입니다.

이처럼 가벼운 구현 덕분에 다양한 플랫폼과 애플리케이션에 쉽게 통합할 수 있습니다.

예시로, iPhone 13에서 완전히 오프라인으로 동작하는 모습을 보여주는 영상이 있습니다: [whisper.objc](examples/whisper.objc)

https://user-images.githubusercontent.com/1991296/197385372-962a6dea-bca1-4d50-bf96-1d8c27b98c81.mp4

또한, 오프라인 음성 비서 애플리케이션도 쉽게 만들 수 있습니다: [command](examples/command)

https://user-images.githubusercontent.com/1991296/204038393-2f846eae-c255-4099-a76d-5735c25c49da.mp4

Apple Silicon에서는 Metal을 통해 완전히 GPU에서 추론이 실행됩니다:

https://github.com/ggml-org/whisper.cpp/assets/1991296/c82e8f86-60dc-49f2-b048-d2fdbd6b5225

---

## 빠른 시작(Quick start)

먼저 저장소를 클론합니다:

```bash
git clone https://github.com/ggml-org/whisper.cpp.git
```

디렉토리로 이동합니다:

```
cd whisper.cpp
```

그런 다음, [`ggml` 포맷](#ggml-format)으로 변환된 Whisper [모델](models/README.md) 중 하나를 다운로드합니다. 예시:

```bash
sh ./models/download-ggml-model.sh base.en
```

이제 [whisper-cli](examples/cli) 예제를 빌드하고 오디오 파일을 다음과 같이 변환할 수 있습니다:

```bash
# 프로젝트 빌드
cmake -B build
cmake --build build -j --config Release

# 오디오 파일 변환
./build/bin/whisper-cli -f samples/jfk.wav
```

---

빠른 데모를 위해서는 `make base.en`을 실행하면 됩니다.

이 명령은 `base.en` 모델을 커스텀 `ggml` 포맷으로 다운로드하고, `samples` 폴더의 모든 `.wav` 샘플에 대해 추론을 실행합니다.

자세한 사용법은 다음을 실행하세요: `./build/bin/whisper-cli -h`

현재 [whisper-cli](examples/cli) 예제는 16비트 WAV 파일만 지원하므로, 실행 전에 입력 파일을 변환해야 합니다.
예를 들어, `ffmpeg`를 다음과 같이 사용할 수 있습니다:

```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 -c:a pcm_s16le output.wav
```

## 추가 오디오 샘플(More audio samples)

추가 오디오 샘플을 사용해보고 싶다면, 다음 명령을 실행하세요:

```
make -j samples
```

이 명령은 Wikipedia에서 몇 개의 오디오 파일을 다운로드하고, `ffmpeg`를 통해 16비트 WAV 포맷으로 변환합니다.

다른 모델을 다운로드하고 실행하려면 다음과 같이 하세요:

```
make -j tiny.en
make -j tiny
make -j base.en
make -j base
make -j small.en
make -j small
make -j medium.en
make -j medium
make -j large-v1
make -j large-v2
make -j large-v3
make -j large-v3-turbo
```

## 메모리 사용량(Memory usage)

| 모델   | 디스크   | 메모리   |
| ------ | ------- | ------- |
| tiny   | 75 MiB  | ~273 MB |
| base   | 142 MiB | ~388 MB |
| small  | 466 MiB | ~852 MB |
| medium | 1.5 GiB | ~2.1 GB |
| large  | 2.9 GiB | ~3.9 GB |

## POWER VSX 명령어 지원(POWER VSX Intrinsics)

`whisper.cpp`는 POWER 아키텍처를 지원하며, Linux에서 POWER9/10에서 동작 시 성능이 크게 향상됩니다. BLAS 패키지를 설치한 후, 표준 cmake 설정 대신 다음을 사용하세요:

```bash
# GGML_BLAS 정의로 빌드
cmake -B build -DGGML_BLAS=1
cmake --build build -j --config Release
./build/bin/whisper-cli [ .. 등등 .. ]
```

## 양자화(Quantization)

`whisper.cpp`는 Whisper `ggml` 모델의 정수 양자화를 지원합니다. 양자화된 모델은 더 적은 메모리와 디스크 공간을 차지하며, 하드웨어에 따라 더 효율적으로 처리될 수 있습니다.

다음은 양자화 모델을 생성하고 사용하는 방법입니다:

```bash
# Q5_0 방식으로 모델 양자화
cmake -B build
cmake --build build -j --config Release
./build/bin/quantize models/ggml-base.en.bin models/ggml-base.en-q5_0.bin q5_0

# 예제 실행 시 양자화 모델 지정
./build/bin/whisper-cli -m models/ggml-base.en-q5_0.bin ./samples/gb0.wav
```

## Core ML 지원(Core ML support)

Apple Silicon 기기에서는 Encoder 추론을 Apple Neural Engine(ANE)에서 실행할 수 있습니다. 이는 CPU만 사용할 때보다 3배 이상 빠를 수 있습니다. Core ML 모델 생성 및 사용법은 다음과 같습니다:

- Core ML 모델 생성을 위한 Python 의존성 설치:

  ```bash
  pip install ane_transformers
  pip install openai-whisper
  pip install coremltools
  ```

  - `coremltools`가 제대로 동작하려면 [Xcode](https://developer.apple.com/xcode/)가 설치되어 있어야 하며, `xcode-select --install`로 커맨드라인 도구를 설치해야 합니다.
  - Python 3.11 권장
  - MacOS Sonoma(버전 14) 이상 권장
  - [선택] Python 버전 관리를 위해 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 사용 권장

- Core ML 모델 생성 예시:

  ```bash
  ./models/generate-coreml-model.sh base.en
  ```

  이 명령은 `models/ggml-base.en-encoder.mlmodelc` 폴더를 생성합니다.

- Core ML 지원으로 whisper.cpp 빌드:

  ```bash
  cmake -B build -DWHISPER_COREML=1
  cmake --build build -j --config Release
  ```

- 예제 실행:

  ```text
  $ ./build/bin/whisper-cli -m models/ggml-base.en.bin -f samples/jfk.wav

  ...

  whisper_init_state: loading Core ML model from 'models/ggml-base.en-encoder.mlmodelc'
  whisper_init_state: first run on a device may take a while ...
  whisper_init_state: Core ML model loaded

  system_info: n_threads = 4 / 10 | AVX = 0 | AVX2 = 0 | AVX512 = 0 | FMA = 0 | NEON = 1 | ARM_FMA = 1 | F16C = 0 | FP16_VA = 1 | WASM_SIMD = 0 | BLAS = 1 | SSE3 = 0 | VSX = 0 | COREML = 1 |

  ...
  ```

첫 실행은 느릴 수 있으며, 이후에는 더 빨라집니다.

자세한 내용은 PR [#566](https://github.com/ggml-org/whisper.cpp/pull/566)을 참고하세요.

## OpenVINO 지원(OpenVINO support)

OpenVINO를 지원하는 플랫폼에서는 Encoder 추론을 x86 CPU 및 Intel GPU에서 실행할 수 있습니다. 성능이 크게 향상될 수 있습니다. OpenVINO 모델 생성 및 사용법은 다음과 같습니다:

- Python 가상환경 및 의존성 설치 (Python 3.10 권장)

  Windows:

  ```powershell
  cd models
  python -m venv openvino_conv_env
  openvino_conv_env\Scripts\activate
  python -m pip install --upgrade pip
  pip install -r requirements-openvino.txt
  ```

  Linux/macOS:

  ```bash
  cd models
  python3 -m venv openvino_conv_env
  source openvino_conv_env/bin/activate
  python -m pip install --upgrade pip
  pip install -r requirements-openvino.txt
  ```

- OpenVINO 인코더 모델 생성 예시:

  ```
  python convert-whisper-to-openvino.py --model base.en
  ```

  이 명령은 ggml-base.en-encoder-openvino.xml/.bin IR 모델 파일을 생성합니다.

- OpenVINO 지원으로 whisper.cpp 빌드:

  OpenVINO 패키지를 [릴리즈 페이지](https://github.com/openvinotoolkit/openvino/releases)에서 다운로드 후 환경설정 및 빌드:

  Linux:

  ```bash
  source /path/to/l_openvino_toolkit_ubuntu22_2023.0.0.10926.b4452d56304_x86_64/setupvars.sh
  ```

  Windows(cmd):

  ```powershell
  C:\Path\To\w_openvino_toolkit_windows_2023.0.0.10926.b4452d56304_x86_64\setupvars.bat
  ```

  빌드:

  ```bash
  cmake -B build -DWHISPER_OPENVINO=1
  cmake --build build -j --config Release
  ```

- 예제 실행:

  ```text
  $ ./build/bin/whisper-cli -m models/ggml-base.en.bin -f samples/jfk.wav

  ...

  whisper_ctx_init_openvino_encoder: loading OpenVINO model from 'models/ggml-base.en-encoder-openvino.xml'
  whisper_ctx_init_openvino_encoder: first run on a device may take a while ...
  whisper_openvino_init: path_model = models/ggml-base.en-encoder-openvino.xml, device = GPU, cache_dir = models/ggml-base.en-encoder-openvino-cache
  whisper_ctx_init_openvino_encoder: OpenVINO model loaded

  system_info: n_threads = 4 / 8 | AVX = 1 | AVX2 = 1 | AVX512 = 0 | FMA = 1 | NEON = 0 | ARM_FMA = 0 | F16C = 1 | FP16_VA = 0 | WASM_SIMD = 0 | BLAS = 0 | SSE3 = 1 | VSX = 0 | COREML = 0 | OPENVINO = 1 |

  ...
  ```

자세한 내용은 PR [#1037](https://github.com/ggml-org/whisper.cpp/pull/1037)을 참고하세요.

## NVIDIA GPU 지원(NVIDIA GPU support)

NVIDIA 그래픽카드에서는 cuBLAS와 커스텀 CUDA 커널을 통해 모델 처리가 효율적으로 GPU에서 이루어집니다. 먼저 [cuda](https://developer.nvidia.com/cuda-downloads)를 설치하세요.

CUDA 지원으로 whisper.cpp 빌드:

```
cmake -B build -DGGML_CUDA=1
cmake --build build -j --config Release
```

최신 NVIDIA GPU(RTX 5000 시리즈 등)에서는 다음과 같이 아키텍처를 지정할 수 있습니다:
```
cmake -B build -DGGML_CUDA=1 -DCMAKE_CUDA_ARCHITECTURES="86"
cmake --build build -j --config Release
```

## Vulkan GPU 지원(Vulkan GPU support)

Vulkan API를 지원하는 그래픽카드에서 GPU 가속을 사용할 수 있습니다.

```
cmake -B build -DGGML_VULKAN=1
cmake --build build -j --config Release
```

## OpenBLAS를 통한 BLAS CPU 가속(BLAS CPU support via OpenBLAS)

OpenBLAS를 설치한 후 다음과 같이 빌드하면 CPU에서 Encoder 처리를 가속할 수 있습니다:

```
cmake -B build -DGGML_BLAS=1
cmake --build build -j --config Release
```

## Ascend NPU 지원(Ascend NPU support)

Ascend NPU는 [`CANN`](https://www.hiascend.com/en/software/cann) 및 AI 코어를 통해 추론 가속을 제공합니다.

지원 기기 확인:

| Ascend NPU                    | 상태    |
|:-----------------------------:|:-------:|
| Atlas 300T A2                 | 지원    |

CANN 툴킷 설치 후 다음과 같이 빌드:

```
cmake -B build -DGGML_CANN=1
cmake --build build -j --config Release
```

예제 실행:

```
./build/bin/whisper-cli -f samples/jfk.wav -m models/ggml-base.en.bin -t 8
```

문제가 있으면 **[CANN]** 태그로 이슈를 남겨주세요.

## Moore Threads GPU 지원(Moore Threads GPU support)

Moore Threads 카드에서는 muBLAS와 커스텀 MUSA 커널을 통해 모델 처리가 효율적으로 GPU에서 이루어집니다. [MUSA SDK rc4.0.1](https://developer.mthreads.com/sdk/download/musa?equipment=&os=&driverVersion=&version=4.0.1) 설치 후 다음과 같이 빌드하세요:

```
cmake -B build -DGGML_MUSA=1
cmake --build build -j --config Release
```

MTT S80 GPU 등 아키텍처 지정 예시:
```
cmake -B build -DGGML_MUSA=1 -DMUSA_ARCHITECTURES="21"
cmake --build build -j --config Release
```

## FFmpeg 지원(Linux only)

Opus, AAC 등 더 많은 오디오 포맷을 지원하려면 `WHISPER_FFMPEG` 빌드 플래그를 활성화하세요.

필요 라이브러리 설치:

```bash
# Debian/Ubuntu
sudo apt install libavcodec-dev libavformat-dev libavutil-dev

# RHEL/Fedora
sudo dnf install libavcodec-free-devel libavformat-free-devel libavutil-free-devel
```

빌드:

```bash
cmake -B build -D WHISPER_FFMPEG=yes
cmake --build build
```

예제:

```bash
# 오디오 파일을 Opus로 변환
ffmpeg -i samples/jfk.wav jfk.opus

# 변환 실행
./build/bin/whisper-cli --model models/ggml-base.en.bin --file jfk.opus
```

## Docker

### 사전 준비

- Docker가 설치되어 실행 중이어야 합니다.
- 모델 및 중간 파일을 저장할 폴더 생성(예: /whisper/models)

### 이미지

이 프로젝트에는 두 가지 Docker 이미지가 있습니다:

1. `ghcr.io/ggml-org/whisper.cpp:main`: 메인 실행 파일, curl, ffmpeg 포함 (플랫폼: `linux/amd64`, `linux/arm64`)
2. `ghcr.io/ggml-org/whisper.cpp:main-cuda`: CUDA 지원 포함 (플랫폼: `linux/amd64`)
3. `ghcr.io/ggml-org/whisper.cpp:main-musa`: MUSA 지원 포함 (플랫폼: `linux/amd64`)

### 사용 예시

```shell
# 모델 다운로드 및 로컬 폴더에 저장
docker run -it --rm \
  -v path/to/models:/models \
  whisper.cpp:main "./models/download-ggml-model.sh base /models"
# 오디오 파일 변환
docker run -it --rm \
  -v path/to/models:/models \
  -v path/to/audios:/audios \
  whisper.cpp:main "whisper-cli -m /models/ggml-base.bin -f /audios/jfk.wav"
# samples 폴더의 오디오 파일 변환
docker run -it --rm \
  -v path/to/models:/models \
  whisper.cpp:main "whisper-cli -m /models/ggml-base.bin -f ./samples/jfk.wav"
```

## Conan으로 설치(Installing with Conan)

[Conan](https://conan.io/)을 사용해 whisper.cpp의 미리 빌드된 바이너리를 설치하거나 소스에서 빌드할 수 있습니다:

```
conan install --requires="whisper-cpp/[∗]" --build=missing
```

자세한 내용은 [Conan 문서](https://docs.conan.io/2/)를 참고하세요.

## 제한사항(Limitations)

- 추론만 지원

## 실시간 오디오 입력 예제(Real-time audio input example)

마이크로폰에서 오디오를 실시간으로 추론하는 예제입니다. [stream](examples/stream) 도구는 0.5초마다 오디오를 샘플링하여 연속적으로 변환합니다. 자세한 내용은 [issue #10](https://github.com/ggml-org/whisper.cpp/issues/10)을 참고하세요. 동작을 위해 [sdl2](https://wiki.libsdl.org/SDL2/Installation)가 필요합니다.

```bash
cmake -B build -DWHISPER_SDL2=ON
cmake --build build -j --config Release
./build/bin/whisper-stream -m ./models/ggml-base.en.bin -t 8 --step 500 --length 5000
```

https://user-images.githubusercontent.com/1991296/194935793-76afede7-cfa8-48d8-a80f-28ba83be7d09.mp4

## 신뢰도 색상 표시(Confidence color-coding)

`--print-colors` 인자를 추가하면, 실험적 색상 코딩 전략으로 신뢰도가 높은/낮은 단어를 색상으로 구분해 출력합니다:

```bash
./build/bin/whisper-cli -m models/ggml-base.en.bin -f samples/gb0.wav --print-colors
```

<img width="965" alt="image" src="https://user-images.githubusercontent.com/1991296/197356445-311c8643-9397-4e5e-b46e-0b4b4daa2530.png">

## 생성 텍스트 세그먼트 길이 제어(실험적)(Controlling the length of the generated text segments (experimental))

예를 들어, 한 줄의 최대 길이를 16자로 제한하려면 `-ml 16`을 추가하세요:

```text
$ ./build/bin/whisper-cli -m ./models/ggml-base.en.bin -f ./samples/jfk.wav -ml 16

whisper_model_load: loading model from './models/ggml-base.en.bin'
...
system_info: n_threads = 4 / 10 | AVX2 = 0 | AVX512 = 0 | NEON = 1 | FP16_VA = 1 | WASM_SIMD = 0 | BLAS = 1 |

main: processing './samples/jfk.wav' (176000 samples, 11.0 sec), 4 threads, 1 processors, lang = en, task = transcribe, timestamps = 1 ...

[00:00:00.000 --> 00:00:00.850]   And so my
[00:00:00.850 --> 00:00:01.590]   fellow
[00:00:01.590 --> 00:00:04.140]   Americans, ask
[00:00:04.140 --> 00:00:05.660]   not what your
[00:00:05.660 --> 00:00:06.840]   country can do
[00:00:06.840 --> 00:00:08.430]   for you, ask
[00:00:08.430 --> 00:00:09.440]   what you can do
[00:00:09.440 --> 00:00:10.020]   for your
[00:00:10.020 --> 00:00:11.000]   country.
```

## 단어 단위 타임스탬프(실험적)(Word-level timestamp (experimental))

`--max-len` 인자를 `-ml 1`로 설정하면 단어 단위 타임스탬프를 얻을 수 있습니다:

```text
$ ./build/bin/whisper-cli -m ./models/ggml-base.en.bin -f ./samples/jfk.wav -ml 1

whisper_model_load: loading model from './models/ggml-base.en.bin'
...
system_info: n_threads = 4 / 10 | AVX2 = 0 | AVX512 = 0 | NEON = 1 | FP16_VA = 1 | WASM_SIMD = 0 | BLAS = 1 |

main: processing './samples/jfk.wav' (176000 samples, 11.0 sec), 4 threads, 1 processors, lang = en, task = transcribe, timestamps = 1 ...

[00:00:00.000 --> 00:00:00.320]
[00:00:00.320 --> 00:00:00.370]   And
[00:00:00.370 --> 00:00:00.690]   so
[00:00:00.690 --> 00:00:00.850]   my
[00:00:00.850 --> 00:00:01.590]   fellow
[00:00:01.590 --> 00:00:02.850]   Americans
[00:00:02.850 --> 00:00:03.300]  ,
[00:00:03.300 --> 00:00:04.140]   ask
[00:00:04.140 --> 00:00:04.990]   not
[00:00:04.990 --> 00:00:05.410]   what
[00:00:05.410 --> 00:00:05.660]   your
[00:00:05.660 --> 00:00:06.260]   country
[00:00:06.260 --> 00:00:06.600]   can
[00:00:06.600 --> 00:00:06.840]   do
[00:00:06.840 --> 00:00:07.010]   for
[00:00:07.010 --> 00:00:08.170]   you
[00:00:08.170 --> 00:00:08.190]  ,
[00:00:08.190 --> 00:00:08.430]   ask
[00:00:08.430 --> 00:00:08.910]   what
[00:00:08.910 --> 00:00:09.040]   you
[00:00:09.040 --> 00:00:09.320]   can
[00:00:09.320 --> 00:00:09.440]   do
[00:00:09.440 --> 00:00:09.760]   for
[00:00:09.760 --> 00:00:10.020]   your
[00:00:10.020 --> 00:00:10.510]   country
[00:00:10.510 --> 00:00:11.000]  .
```

## tinydiarize를 통한 화자 분리(실험적)(Speaker segmentation via tinydiarize (experimental))

자세한 내용은 https://github.com/ggml-org/whisper.cpp/pull/1058 을 참고하세요.

사용 예시:

```py
# tinydiarize 호환 모델 다운로드
./models/download-ggml-model.sh small.en-tdrz

# -tdrz 인자 추가하여 실행
./build/bin/whisper-cli -f ./samples/a13.wav -m ./models/ggml-small.en-tdrz.bin -tdrz
...
main: processing './samples/a13.wav' (480000 samples, 30.0 sec), 4 threads, 1 processors, lang = en, task = transcribe, tdrz = 1, timestamps = 1 ...
...
[00:00:00.000 --> 00:00:03.800]   Okay Houston, we've had a problem here. [SPEAKER_TURN]
[00:00:03.800 --> 00:00:06.200]   This is Houston. Say again please. [SPEAKER_TURN]
[00:00:06.200 --> 00:00:08.260]   Uh Houston we've had a problem.
[00:00:08.260 --> 00:00:11.320]   We've had a main beam up on a volt. [SPEAKER_TURN]
[00:00:11.320 --> 00:00:13.820]   Roger main beam interval. [SPEAKER_TURN]
[00:00:13.820 --> 00:00:15.100]   Uh uh [SPEAKER_TURN]
[00:00:15.100 --> 00:00:18.020]   So okay stand, by thirteen we're looking at it. [SPEAKER_TURN]
[00:00:18.020 --> 00:00:25.740]   Okay uh right now uh Houston the uh voltage is uh is looking good um.
[00:00:27.620 --> 00:00:29.940]   And we had a a pretty large bank or so.
```

## 노래방 스타일 영상 생성(실험적)(Karaoke-style movie generation (experimental))

[whisper-cli](examples/cli) 예제는 노래방 스타일 영상 출력을 지원합니다. `-owts` 인자를 사용하고, 생성된 bash 스크립트를 실행하세요. `ffmpeg`가 필요합니다.

예시:

```bash
./build/bin/whisper-cli -m ./models/ggml-base.en.bin -f ./samples/jfk.wav -owts
source ./samples/jfk.wav.wts
ffplay ./samples/jfk.wav.mp4
```

https://user-images.githubusercontent.com/1991296/199337465-dbee4b5e-9aeb-48a3-b1c6-323ac4db5b2c.mp4

---

```bash
./build/bin/whisper-cli -m ./models/ggml-base.en.bin -f ./samples/mm0.wav -owts
source ./samples/mm0.wav.wts
ffplay ./samples/mm0.wav.mp4
```

https://user-images.githubusercontent.com/1991296/199337504-cc8fd233-0cb7-4920-95f9-4227de3570aa.mp4

---

```bash
./build/bin/whisper-cli -m ./models/ggml-base.en.bin -f ./samples/gb0.wav -owts
source ./samples/gb0.wav.wts
ffplay ./samples/gb0.wav.mp4
```

https://user-images.githubusercontent.com/1991296/199337538-b7b0c7a3-2753-4a88-a0cd-f28a317987ba.mp4

---

## 다양한 모델 비교 영상(Video comparison of different models)

[scripts/bench-wts.sh](https://github.com/ggml-org/whisper.cpp/blob/master/scripts/bench-wts.sh) 스크립트를 사용해 다음과 같은 형식의 영상을 생성할 수 있습니다:

```bash
./scripts/bench-wts.sh samples/jfk.wav
ffplay ./samples/jfk.wav.all.mp4
```

https://user-images.githubusercontent.com/1991296/223206245-2d36d903-cf8e-4f09-8c3b-eb9f9c39d6fc.mp4

---

## 벤치마크(Benchmarks)

시스템별 성능 비교를 위해 [whisper-bench](examples/bench) 도구를 사용하세요. Encoder 부분만 실행하여 소요 시간을 출력합니다. 결과는 다음 이슈에 정리되어 있습니다:

[Benchmark results](https://github.com/ggml-org/whisper.cpp/issues/89)

여러 모델과 오디오 파일을 대상으로 벤치마크하는 [bench.py](scripts/bench.py)도 제공됩니다.

```bash
python3 scripts/bench.py -f samples/jfk.wav -t 2,4,8 -p 1,2
```

결과는 csv 파일로 출력됩니다.

## `ggml` 포맷

원본 모델은 커스텀 바이너리 포맷으로 변환됩니다. 이 포맷에는 다음이 모두 포함됩니다:

- 모델 파라미터
- mel 필터
- 어휘
- 가중치

변환된 모델은 [models/download-ggml-model.sh](models/download-ggml-model.sh) 스크립트나 아래 링크에서 다운로드할 수 있습니다:

- https://huggingface.co/ggerganov/whisper.cpp

자세한 내용은 [models/convert-pt-to-ggml.py](models/convert-pt-to-ggml.py) 또는 [models/README.md](models/README.md)를 참고하세요.

## [바인딩(Bindings)](https://github.com/ggml-org/whisper.cpp/discussions/categories/bindings)

- [x] Rust: [tazz4843/whisper-rs](https://github.com/tazz4843/whisper-rs) | [#310](https://github.com/ggml-org/whisper.cpp/discussions/310)
- [x] JavaScript: [bindings/javascript](bindings/javascript) | [#309](https://github.com/ggml-org/whisper.cpp/discussions/309)
  - React Native (iOS / Android): [whisper.rn](https://github.com/mybigday/whisper.rn)
- [x] Go: [bindings/go](bindings/go) | [#312](https://github.com/ggml-org/whisper.cpp/discussions/312)
- [x] Java:
  - [GiviMAD/whisper-jni](https://github.com/GiviMAD/whisper-jni)
- [x] Ruby: [bindings/ruby](bindings/ruby) | [#507](https://github.com/ggml-org/whisper.cpp/discussions/507)
- [x] Objective-C / Swift: [ggml-org/whisper.spm](https://github.com/ggml-org/whisper.spm) | [#313](https://github.com/ggml-org/whisper.cpp/discussions/313)
  - [exPHAT/SwiftWhisper](https://github.com/exPHAT/SwiftWhisper)
- [x] .NET: | [#422](https://github.com/ggml-org/whisper.cpp/discussions/422)
  - [sandrohanea/whisper.net](https://github.com/sandrohanea/whisper.net)
  - [NickDarvey/whisper](https://github.com/NickDarvey/whisper)
- [x] Python: | [#9](https://github.com/ggml-org/whisper.cpp/issues/9)
  - [stlukey/whispercpp.py](https://github.com/stlukey/whispercpp.py) (Cython)
  - [AIWintermuteAI/whispercpp](https://github.com/AIWintermuteAI/whispercpp) (aarnphm/whispercpp의 업데이트 포크)
  - [aarnphm/whispercpp](https://github.com/aarnphm/whispercpp) (Pybind11)
  - [abdeladim-s/pywhispercpp](https://github.com/abdeladim-s/pywhispercpp) (Pybind11)
- [x] R: [bnosac/audio.whisper](https://github.com/bnosac/audio.whisper)
- [x] Unity: [macoron/whisper.unity](https://github.com/Macoron/whisper.unity)

## XCFramework
XCFramework는 iOS, visionOS, tvOS, macOS용으로 미리 컴파일된 라이브러리입니다. Swift 프로젝트에서 소스 빌드 없이 사용할 수 있습니다. 예시:

```swift
// swift-tools-version: 5.10
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "Whisper",
    targets: [
        .executableTarget(
            name: "Whisper",
            dependencies: [
                "WhisperFramework"
            ]),
        .binaryTarget(
            name: "WhisperFramework",
            url: "https://github.com/ggml-org/whisper.cpp/releases/download/v1.7.5/whisper-v1.7.5-xcframework.zip",
            checksum: "c7faeb328620d6012e130f3d705c51a6ea6c995605f2df50f6e1ad68c59c6c4a"
        )
    ]
)
```

## 음성 활동 감지(VAD)

`whisper-cli`에서 `--vad` 인자를 사용해 음성 활동 감지(VAD)를 활성화할 수 있습니다. 별도의 VAD 모델이 필요합니다.

동작 방식: 오디오 샘플을 먼저 VAD 모델에 통과시켜 음성 구간을 감지합니다. 감지된 구간만 Whisper로 전달하여 처리량을 줄이고 속도를 높입니다.

### Silero-VAD
[Silero-vad](https://github.com/snakers4/silero-vad)는 Python으로 작성된 경량 VAD 모델입니다.

Linux/MacOS에서 모델 다운로드:
```console
$ ./models/download-vad-model.sh silero-v5.1.2
```
Windows에서:
```console
> .\models\download-vad-model.cmd silero-v5.1.2
```

수동 변환 예시:
```console
$ python3 -m venv venv && source venv/bin/activate
$ (venv) pip install silero-vad
$ (venv) $ python models/convert-silero-vad-to-ggml.py --output models/silero.bin
```
사용 예시:
```console
$ ./build/bin/whisper-cli \
   --file ./samples/jfk.wav \
   --model ./models/ggml-base.en.bin \
   --vad \
   --vad-model ./models/silero-v5.1.2-ggml.bin
```

#### VAD 옵션

* --vad-threshold: 음성 감지 임계값
* --vad-min-speech-duration-ms: 최소 음성 구간(ms)
* --vad-min-silence-duration-ms: 최소 무음 구간(ms)
* --vad-max-speech-duration-s: 최대 음성 구간(s)
* --vad-speech-pad-ms: 음성 구간 앞뒤 패딩(ms)
* --vad-samples-overlap: 구간 간 오디오 중첩(초)

## 예제(Examples)

[examples](examples) 폴더에 다양한 예제가 있습니다. 일부는 WebAssembly로 브라우저에서도 동작합니다.

| 예제                                               | Web                                   | 설명                                                                                 |
| --------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------ |
| [whisper-cli](examples/cli)                         | [whisper.wasm](examples/whisper.wasm) | Whisper를 이용한 오디오 번역 및 변환 도구                                            |
| [whisper-bench](examples/bench)                     | [bench.wasm](examples/bench.wasm)     | 시스템 성능 벤치마크                                                                 |
| [whisper-stream](examples/stream)                   | [stream.wasm](examples/stream.wasm)   | 마이크 실시간 변환                                                                   |
| [whisper-command](examples/command)                 | [command.wasm](examples/command.wasm) | 음성 명령어 인식 예제                                                                |
| [whisper-server](examples/server)                   |                                       | HTTP 변환 서버                                                                       |
| [whisper-talk-llama](examples/talk-llama)           |                                       | LLaMA 봇과 대화                                                                      |
| [whisper.objc](examples/whisper.objc)               |                                       | iOS 모바일 앱                                                                        |
| [whisper.swiftui](examples/whisper.swiftui)         |                                       | SwiftUI iOS / macOS 앱                                                               |
| [whisper.android](examples/whisper.android)         |                                       | Android 모바일 앱                                                                    |
| [whisper.nvim](examples/whisper.nvim)               |                                       | Neovim용 음성-텍스트 플러그인                                                        |
| [generate-karaoke.sh](examples/generate-karaoke.sh) |                                       | [노래방 영상 생성](https://youtu.be/uj7hVta4blM)                                     |
| [livestream.sh](examples/livestream.sh)             |                                       | [라이브 오디오 변환](https://github.com/ggml-org/whisper.cpp/issues/185)              |
| [yt-wsp.sh](examples/yt-wsp.sh)                     |                                       | VOD 다운로드+변환 [(원본)](https://gist.github.com/DaniruKun/96f763ec1a037cc92fe1a059b643b818) |
| [wchess](examples/wchess)                           | [wchess.wasm](examples/wchess)        | 음성 제어 체스                                                                       |

## [토론(Discussions)](https://github.com/ggml-org/whisper.cpp/discussions)

이 프로젝트에 대한 피드백은 Discussions 섹션에 남겨주세요. [Show and tell](https://github.com/ggml-org/whisper.cpp/discussions/categories/show-and-tell) 카테고리에서 본인 프로젝트를 공유할 수 있습니다. 질문이 있다면 [자주 묻는 질문(#126)](https://github.com/ggml-org/whisper.cpp/discussions/126)도 참고하세요.
