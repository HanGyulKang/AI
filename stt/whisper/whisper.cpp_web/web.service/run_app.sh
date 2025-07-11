#!/bin/bash

# Streamlit 앱 실행 스크립트
# 사용법: ./run_app.sh

echo "🚀 Whisper.cpp 웹 서비스 시작 중..."

# 현재 디렉토리를 스크립트가 있는 디렉토리로 변경
cd "$(dirname "$0")"

# 상위 디렉토리로 이동 (whisper-cli와 model 폴더가 있는 곳)
cd ..

# Python 가상환경 확인 (선택사항)
# if [ -d "venv" ]; then
#     echo "가상환경 활성화 중..."
#     source venv/bin/activate
# fi

# 필요한 패키지 설치
echo "📦 필요한 패키지 설치 중..."
pip install -r web.service/requirements.txt

# Streamlit 앱 실행
echo "🌐 웹 서비스 시작 중..."
echo "브라우저에서 http://localhost:8501 을 열어주세요"
echo "종료하려면 Ctrl+C를 누르세요"
echo ""

streamlit run web.service/app.py --server.port 8501 --server.address 0.0.0.0 