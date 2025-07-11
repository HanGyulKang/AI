# Whisper.cpp CUDA build GUide : Window 11

---

### 1. 필수 프로그램 목록
* [GNU make](https://gnuwin32.sourceforge.net/packages/make.htm)
  * 3.81 이상
* [CMake]((https://cmake.org/download/))
  * 4.0.3 이상
* [Visual Studio 2022]((https://visualstudio.microsoft.com/ko/thank-you-downloading-visual-studio/?sku=Community&channel=Release&version=VS2022&source=VSLandingPage&cid=2030&passive=false))
  * C++, C 관련 프로그램 설치
* [Cuda toolkit 12.4.0 Version 이상]((https://developer.nvidia.com/cuda-downloads))
* [Git](https://git-scm.com/downloads/win)


### 2. 환경 변수
* **CUDA_PATH**
  * ex) C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4
  * Cuda Toolkit 설치 시 자동으로 잡아주기도 함

* **CUDA_PATH_V**{Version} : ex) CUDA_PATH_V12_4
  * ex) C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4
  * Cuda Toolkit 설치 시 자동으로 잡아주기도 함

* **Path**
  * **Cuda Toolkit 관련**
    * C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\bin
    * C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.4\libnvvp

  * **GNU make**
    * C:\Program Files (x86)\GnuWin32\bin

  * **CMake**
    * C:\Program Files\CMake\bin

  * **Visual Studio**
    * C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\b

### #. Whisper 실행
* 기존 `Makefile` 코드 수정 필요
* 한 줄로 적으면 됨
* 예시의 모든 경로는 사용자 PC환경에 따라 달라질 수 있음

#### 기본 옵션
* `cmake -B build`: 빌드 디렉토리를 `build`로 지정

#### 빌드 시스템 지정
* `-G "Visual Studio 17 2022"`: Visual Studio 2022를 빌드 시스템으로 지정  (환경변수 설정이 적용 안 될 때 수동 지정)

#### 아키텍처 설정
* `-A x64`: 64비트 x64 아키텍처로 빌드

#### 라이브러리 빌드 타입
* `-DBUILD_SHARED_LIBS=OFF`: 공유 라이브러리(DLL) 빌드 비활성화
* `-DBUILD_STATIC_LIBS=ON`: 정적 라이브러리(.lib) 빌드 활성화

#### CUDA 설정

* `-DGGML_CUDA=1`: CUDA 백엔드 활성화 (GPU 가속 사용)
* `-DCMAKE_CUDA_ARCHITECTURES="89"`: CUDA 아키텍처를 8.9로 지정 (RTX 5060 Ti에 맞는 설정)
* `-DCUDAToolkit_ROOT="C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.4"`: CUDA Toolkit 경로 명시적 지정 (환경변수 설정이 적용 안 될 때 수동 지정)

#### 런타임 라이브러리 설정

* `-DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded`: 정적 멀티스레드 런타임 라이브러리 사용 (/MT 플래그와 동일)

#### Metal 라이브러리 설정

* `-DGGML_METAL_EMBED_LIBRARY=OFF`: Metal 라이브러리를 정적으로 임베드하지 않음 (Windows에서 불필요한 Metal 코드 제외)

#### 전체 명령어의 목적

이 설정들은 **완전한 정적 빌드**를 만들어서 `whisper-cli.exe`가 다른 시스템에서도 `DLL` 의존성 없이 실행될 수 있도록 하는 것이 목적

##### 특히 필수:
* `BUILD_SHARED_LIBS=OFF` + `BUILD_STATIC_LIBS=ON`: 정적 링크 강제
* `CMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded`: 런타임 라이브러리도 정적으로 링크
* `GGML_METAL_EMBED_LIBRARY=OFF`: 불필요한 Metal 코드 제외로 파일 크기 최적화

#### 기타

정적빌드는 필요한 상황에만 하면 되기 때문에 Optional함

#### 결과
```yaml
.PHONY: build
build:
    cmake -B build -G "Visual Studio 17 2022" -A x64 -DBUILD_SHARED_LIBS=OFF -DBUILD_STATIC_LIBS=ON -DGGML_CUDA=1 -DCMAKE_CUDA_ARCHITECTURES="89" -DCUDAToolkit_ROOT="C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.4" -DCMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded -DGGML_METAL_EMBED_LIBRARY=OFF
    cmake --build build --config Release
```

