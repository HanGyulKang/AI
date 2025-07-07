# Whisper.cpp 웹 서비스

이 웹 서비스는 Whisper.cpp를 사용하여 음성 파일을 실시간으로 텍스트로 변환하는 Streamlit 애플리케이션입니다.

## 기능

- 🎵 다양한 오디오/비디오 형식 지원 (mp3, wav, m4a, flac, ogg, mp4, avi, mov, webm)
- 🌍 다국어 지원 (한국어, 영어, 일본어, 중국어)
- ⚡ 실시간 스트리밍 변환 결과
- 📥 변환된 텍스트 파일 다운로드
- 🎨 직관적인 웹 인터페이스

## 설치 및 실행

### 1. 실행 스크립트 사용 (권장)

```bash
# 실행 권한 부여
chmod +x run_app.sh

# 웹 서비스 시작
./run_app.sh
```

### 2. 수동 실행

```bash
# 필요한 패키지 설치
pip install -r requirements.txt

# Streamlit 앱 실행
streamlit run app.py --server.port 8501
```

## 사용법

1. 웹 브라우저에서 `http://localhost:8501` 접속
2. "파일 업로드" 영역에서 음성 파일 선택
3. 언어 선택 (기본값: 한국어)
4. "변환 시작" 버튼 클릭
5. 실시간으로 변환 결과 확인
6. 완료 후 텍스트 파일 다운로드 가능

## 시스템 요구사항

- Python 3.7 이상
- Whisper.cpp 실행 파일 (`whisper-cli`)
- GGML 모델 파일 (`models/ggml-large-v2.bin`)
- 최소 4GB RAM (모델 로딩용)

## 파일 구조

```
web.service/
├── app.py              # Streamlit 메인 애플리케이션
├── requirements.txt    # Python 패키지 의존성
├── run_app.sh         # 실행 스크립트
└── README.md          # 이 파일
```

## 문제 해결

### 오류: "whisper-cli not found"
- `whisper-cli` 실행 파일이 상위 디렉토리에 있는지 확인
- 실행 권한이 있는지 확인: `chmod +x ../whisper-cli`

### 오류: "Model file not found"
- `models/ggml-large-v2.bin` 파일이 상위 디렉토리의 models 폴더에 있는지 확인

### 성능 최적화
- 큰 파일의 경우 변환 시간이 오래 걸릴 수 있습니다
- SSD 사용을 권장합니다
- 충분한 RAM 확보 (8GB 이상 권장) 