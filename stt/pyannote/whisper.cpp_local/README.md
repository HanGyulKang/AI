### 한국어를 위해 fine-tuning된 모델을 받아서 처리

* **`git-lfs`** 설치 필수

#### git clone
- git@github.com:ggerganov/whisper.cpp.git
- https://github.com/openai/whisper
- https://huggingface.co/seastar105/whisper-medium-ko-zeroth <!-- ko fine tunning model -->

1. 세 개를 한 폴더에 clone 받는다
2. `python3 ./whisper.cpp/models/convert-h5-to-ggml.py ./whisper-medium-ko-zeroth ./whisper .` 를 실행해서 fine tunning model을 받는다`ggml-model.bin`파일이 생성 됨.
3. 위의 `bin` 파일을 whisper.cpp 폴더의 models 폴더 안에 넣는다.
4. `whisper.cpp` 폴더 안에서 `make`(없다면 설치하면 됨 `brew install make`)명령어를 실행하면 `build/bin` 폴더 안에 `whisper-cli` 파일이 생기는데 해당 파일로 모델을 실행하면 됨

> ./whisper-cli -l ko -m models/{model-name}.bin -f {path}/{audio-file-name}.{extension}

5. 다른 모델을 사용해보고 싶으면 `make` 명령어로 만들면 됨

> make {model-name}

##### 현재 기준 지원하는 모델
```
tiny.en
tiny
base.en
base
small.en
small
medium.en
medium
large-v1
large-v2
large-v3
large-v3-turbo
```

##### GGML은 지원하는 모델이 더 있음
```
tiny
tiny.en
tiny-q5_1
tiny.en-q5_1
tiny-q8_0
base
base.en
base-q5_1
base.en-q5_1

base-q8_0
small
small.en
small.en-tdrz
small-q5_1
small.en-q5_1
small-q8_0
medium
medium.en
medium-q5_0
medium.en-q5_0
medium-q8_0
large-v1
large-v2
large-v2-q5_0
large-v2-q8_0
large-v3
large-v3-q5_0
large-v3-turbo
large-v3-turbo-q5_0
large-v3-turbo-q8_0
```

6. 모델을 생성하게 되면 `whisper.cpp/models` 에 `.bin`파일로 생성 됨
7. 그러면 `whisper-cli` 파일과 `.bin` 형식의 모델만 있으면 로컬에서 인터넷 연결 없이 `STT AI` 실행이 가능 함
8. `CPU`나 `GPU`를 활용하는건 알아서 해주는 것으로 확인 됨
9. 한국어 변환은 `large-v3`보다 `large-v2`가 훨씬 좋음
10. 모델명 뒤에 tdrz 붙어있는데 화자분리 해주는 모델들인데 영문밖에 없음 ㅠ

---

`Whisper.cpp`의 경우 빌드를 할 때 로컬 PC 하드웨어 정보 기반으로 빌드를 하는 것으로 확인 됨  
그래서 정적 빌드 `-DBUILD_SHARED_LIBS=OFF` 를 하더라도 `whisper-cli`또는 `whisper-cli.exe` 파일을 다른 PC로 가져가면  
기존에 수집한 하드웨어 정보와 달라서 실행은 되나 동작은 하지 않음