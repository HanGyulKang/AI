import streamlit as st
import subprocess
import tempfile
import os
import threading
import time
import queue
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="Whisper.cpp 음성-텍스트 변환기",
    page_icon="",
    layout="wide"
)

# 제목
st.title(" Whisper.cpp 음성-텍스트 변환기")
st.markdown("---")

# 전역 변수로 결과 저장 (스레드 안전)
global_result_queue = queue.Queue()
global_result_ready = False
global_result_data = None
global_result_type = None

# 사이드바 설정
with st.sidebar:
    st.header("설정")
    language = st.selectbox(
        "언어 선택",
        ["ko", "en", "ja", "zh"],
        index=0,
        help="음성 파일의 언어를 선택하세요"
    )
    
    st.markdown("---")
    st.markdown("### 지원 형식")
    st.markdown("- 오디오: mp3, wav, m4a, flac, ogg")
    st.markdown("- 비디오: mp4, avi, mov, webm")
    
    st.markdown("---")
    st.markdown("### 모델 정보")
    st.markdown("- **모델**: ggml-large-v2")
    st.markdown("- **정확도**: 높음")
    st.markdown("- **속도**: 중간")

# 메인 영역
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📁 파일 업로드")
    
    # 파일 업로드
    uploaded_file = st.file_uploader(
        "음성 파일을 선택하세요",
        type=['mp3', 'wav', 'm4a', 'flac', 'ogg', 'mp4', 'avi', 'mov', 'webm'],
        help="지원되는 오디오/비디오 파일을 업로드하세요"
    )

with col2:
    st.header("🎵 음원 재생")
    
    if uploaded_file is not None:
        # 음원 재생 컴포넌트
        st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')
        
        # 파일 정보 표시
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        st.info(f"📄 파일명: {uploaded_file.name}")
        st.info(f"📊 파일 크기: {file_size:.2f} MB")
    else:
        st.info("파일을 업로드하면 여기에 음원 재생기가 표시됩니다")

# 변환 버튼
if uploaded_file is not None and not st.session_state.get('processing', False):
    if st.button("🚀 변환 시작", type="primary", use_container_width=True):
        st.session_state.processing = True
        st.session_state.transcription_text = ""
        st.rerun()

# 텍스트 결과 영역
st.markdown("---")
st.header("📝 변환 결과")

# 결과를 표시할 placeholder 생성
result_placeholder = st.empty()

# 결과 처리 (매 프레임마다 체크) - 메인 스레드에서 실행
if global_result_ready == True:
    if global_result_type == "success":
        # placeholder에 직접 결과 표시
        with result_placeholder.container():
            st.text_area(
                "변환된 텍스트",
                value=global_result_data,
                height=400,
                disabled=True
            )
            
            # 다운로드 버튼
            st.download_button(
                label="📥 텍스트 파일 다운로드",
                data=global_result_data,
                file_name=f"transcription_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        st.session_state.processing = False
        # 전역 변수 초기화
        global_result_ready = False
        global_result_data = None
        global_result_type = None
        
    elif global_result_type == "error":
        with result_placeholder.container():
            st.error(global_result_data)
        st.session_state.processing = False
        # 전역 변수 초기화
        global_result_ready = False
        global_result_data = None
        global_result_type = None

# 초기 상태 또는 처리 중일 때 placeholder에 기본 내용 표시
if not global_result_ready:
    with result_placeholder.container():
        if st.session_state.get('processing', False):
            with st.spinner("음성을 텍스트로 변환 중입니다..."):
                st.info("변환이 완료되면 결과가 표시됩니다.")
        else:
            st.text_area(
                "변환된 텍스트가 여기에 표시됩니다",
                value="",
                height=400,
                disabled=True
            )

def process_audio_file(file_path, language):
    """음성 파일을 처리하는 함수"""
    global global_result_ready, global_result_data, global_result_type
    
    try:
        # 현재 스크립트의 디렉토리를 기준으로 경로 설정
        script_dir = Path(__file__).parent.absolute()
        whisper_cli_path = script_dir / "whisper-cli"
        model_path = script_dir.parent / "model" / "ggml-large-v2-q8_0.bin"
        
        # 파일 존재 확인
        if not whisper_cli_path.exists():
            raise FileNotFoundError(f"whisper-cli 파일을 찾을 수 없습니다: {whisper_cli_path}")
        
        if not model_path.exists():
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {model_path}")
        
        # whisper-cli 실행
        cmd = [
            str(whisper_cli_path),
            "-l", language,
            "-m", str(model_path),
            "-f", file_path
        ]
        
        # 명령어 로깅 (디버깅용)
        print(f"실행 명령어: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        transcription_lines = []
        processing_started = False
        
        # 실시간으로 출력 읽기
        for line in process.stdout:
            print(f"{line.strip()}")  # 디버깅용
            
            # "main: processing" 메시지가 나오면 처리 시작
            if "main: processing" in line:
                processing_started = True
                continue
            
            # "ggml_metal_free: deallocating" 메시지가 나오면 처리 완료
            if "ggml_metal_free: deallocating" in line:
                process.returncode = 0
                break
            
            # 처리 중이고 타임라인이 있는 라인만 수집
            if processing_started and "[" in line and "-->" in line and "]" in line:
                # "Whisper 출력: " 부분을 제거하고 타임라인부터 내용까지 추출
                clean_line = line.strip()
                transcription_lines.append(clean_line + "\n")

        process.wait()
        
        if process.returncode == 0:
        # 전역 변수에 결과 저장
            result_text = "".join(transcription_lines)
            global_result_data = result_text
            global_result_type = "success"
            global_result_ready = True
        else:
            global_result_data = "음성 변환 중 오류가 발생했습니다."
            global_result_type = "error"
            global_result_ready = True
            
    except Exception as e:
        error_msg = f"처리 중 오류가 발생했습니다: {str(e)}"
        print(error_msg)  # 디버깅용
        global_result_data = error_msg
        global_result_type = "error"
        global_result_ready = True

# 파일이 업로드되고 변환이 시작되었을 때 처리
if uploaded_file is not None and st.session_state.get('processing', False):
    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    # 백그라운드에서 처리
    thread = threading.Thread(
        target=process_audio_file,
        args=(tmp_file_path, language)
    )
    thread.start()
    
    # 스레드가 완료될 때까지 대기 (블로킹)
    thread.join()
    
    # 스레드 완료 후 결과 처리
    if global_result_ready:
        if global_result_type == "success":
            with result_placeholder.container():
                st.text_area(
                    "변환된 텍스트",
                    value=global_result_data,
                    height=400,
                    disabled=True
                )
                # ... 다운로드 버튼
            st.session_state.processing = False
        elif global_result_type == "error":
            with result_placeholder.container():
                st.error(global_result_data)
            st.session_state.processing = False
    
    # 임시 파일 정리
    try:
        os.unlink(tmp_file_path)
    except:
        pass
