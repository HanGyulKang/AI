import os
import subprocess
import argparse
import tempfile
from pydub import AudioSegment
from datetime import datetime
import numpy as np
import webrtcvad
import sounddevice as sd
import soundfile as sf

def has_speech(audio_data, sample_rate=16000):
    """
    음성이 있는지 확인하는 함수
    """
    vad = webrtcvad.Vad(2)  # 민감도 설정 (0-3)
    
    # 30ms 프레임으로 분할
    frame_duration = 30  # ms
    frame_size = int(sample_rate * frame_duration / 1000)
    
    has_speech_frames = 0
    total_frames = 0
    
    for i in range(0, len(audio_data) - frame_size, frame_size):
        frame = audio_data[i:i + frame_size]
        if len(frame) == frame_size:
            is_speech = vad.is_speech(frame.tobytes(), sample_rate)
            if is_speech:
                has_speech_frames += 1
            total_frames += 1
    
    # 50% 이상의 프레임에서 음성이 감지되면 True
    return (has_speech_frames / total_frames) > 0.5 if total_frames > 0 else False

def record_audio_with_vad(duration=5, sample_rate=16000):
    """
    음성 활동 감지를 포함한 오디오 녹음
    """
    print(f"🎤 {duration}초 동안 녹음 중... (말씀해주세요)")
    
    audio_data = sd.rec(int(duration * sample_rate), 
                       samplerate=sample_rate, 
                       channels=1, 
                       dtype='int16')
    sd.wait()
    
    # 음성 활동 감지
    if has_speech(audio_data, sample_rate):
        print("✅ 음성 감지됨!")
        return audio_data
    else:
        print("음성이 감지되지 않았습니다. 다시 시도해주세요.")
        return None

def record_audio(duration=5, sample_rate=16000):
    """
    마이크에서 오디오를 녹음하는 함수 (sounddevice 사용)
    
    Args:
        duration (int): 녹음 시간 (초)
        sample_rate (int): 샘플링 레이트
    
    Returns:
        numpy.ndarray: 녹음된 오디오 데이터
    """
    print(f"🎤 {duration}초 동안 녹음 중... (말씀해주세요)")
    
    # 오디오 녹음
    audio_data = sd.rec(int(duration * sample_rate), 
                       samplerate=sample_rate, 
                       channels=1, 
                       dtype='int16')
    sd.wait()  # 녹음 완료까지 대기
    
    print("✅ 녹음 완료!")
    return audio_data

def save_audio_to_wav(audio_data, file_path, sample_rate=16000):
    """
    오디오 데이터를 WAV 파일로 저장하는 함수
    
    Args:
        audio_data (numpy.ndarray): 오디오 데이터
        file_path (str): 저장할 파일 경로
        sample_rate (int): 샘플링 레이트
    """
    sf.write(file_path, audio_data, sample_rate)

def process_audio_file(input_file_path, output_dir=None):
    """
    오디오 파일을 처리하여 텍스트로 변환하는 함수
    
    Args:
        input_file_path (str): 입력 오디오 파일 경로
        output_dir (str): 출력 디렉토리 (기본값: 입력 파일과 같은 디렉토리)
    """
    
    # 파일 존재 확인
    if not os.path.exists(input_file_path):
        print(f"오류: 파일을 찾을 수 없습니다: {input_file_path}")
        return None
    
    # 출력 디렉토리 설정
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(input_file_path))
    
    # 출력 디렉토리가 없으면 생성
    os.makedirs(output_dir, exist_ok=True)
    
    # 현재 스크립트의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # whisper.cpp 경로 설정
    whisper_cli_path = os.path.join(current_dir, "..", "pyannote", "whisper.cpp_local", "whisper-cli")
    model_path = os.path.join(current_dir, "..", "pyannote", "whisper.cpp_local", "model", "ggml-large-v2-q8_0.bin")
    
    # whisper.cpp 실행 파일 존재 확인
    if not os.path.exists(whisper_cli_path):
        print(f"오류: whisper-cli를 찾을 수 없습니다: {whisper_cli_path}")
        print("whisper.cpp가 설치되어 있는지 확인해주세요.")
        return None
    
    # 모델 파일 존재 확인
    if not os.path.exists(model_path):
        print(f"오류: 모델 파일을 찾을 수 없습니다: {model_path}")
        print("whisper.cpp 모델이 다운로드되어 있는지 확인해주세요.")
        return None
    
    try:
        print(f"오디오 파일 처리 중: {input_file_path}")
        
        # 1. 오디오 파일 로드
        print("오디오 파일 로드 중...")
        audio = AudioSegment.from_file(input_file_path)
        print(f"오디오 정보 - 길이: {len(audio)}ms, 샘플링 레이트: {audio.frame_rate}Hz")
        
        # 2. 노이즈 제거 (Low-pass filter 3000Hz)
        print("노이즈 제거 중 (Low-pass filter 3000Hz)...")
        audio = audio.low_pass_filter(3000)
        print("노이즈 제거 완료")
        
        # 3. 볼륨 높이기 (+5 dB)
        print("볼륨을 5dB 증폭 중...")
        audio = audio + 5
        print("볼륨 증폭 완료")
        
        # 4. 처리된 오디오를 임시 WAV 파일로 저장
        input_filename = os.path.splitext(os.path.basename(input_file_path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_wav_file = os.path.join(output_dir, f"{input_filename}_processed_{timestamp}.wav")
        
        print(f"처리된 오디오를 임시 파일로 저장 중: {temp_wav_file}")
        audio.export(temp_wav_file, format="wav")
        print("임시 파일 저장 완료")
        
        # 5. whisper.cpp로 텍스트 변환
        print("whisper.cpp로 텍스트 변환 중...")
        whisper_cmd = [
            whisper_cli_path,
            "-l", "ko",
            "-m", model_path,
            temp_wav_file
        ]
        
        result = subprocess.run(whisper_cmd, 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(whisper_cli_path))
        
        if result.returncode == 0:
            transcribed_text = result.stdout.strip()
            
            # 6. 결과를 텍스트 파일로 저장
            output_text_file = os.path.join(output_dir, f"{input_filename}_transcript_{timestamp}.txt")
            
            with open(output_text_file, 'w', encoding='utf-8') as f:
                f.write(f"=== 오디오 파일: {input_file_path} ===\n")
                f.write(f"=== 처리 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
                f.write("=== 변환된 텍스트 ===\n")
                f.write(transcribed_text)
                f.write("\n")
            
            print(f"\n=== 변환 완료 ===")
            print(f"입력 파일: {input_file_path}")
            print(f"출력 텍스트 파일: {output_text_file}")
            print(f"변환된 텍스트:\n{transcribed_text}")
            
            # 7. 임시 WAV 파일 삭제
            os.remove(temp_wav_file)
            print(f"임시 파일 삭제 완료: {temp_wav_file}")
            
            return output_text_file
            
        else:
            print(f"whisper.cpp 실행 실패:")
            print(f"오류 메시지: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"오류 발생: {e}")
        return None

def process_realtime_audio():
    """
    실시간 마이크 입력을 처리하는 함수 (볼륨 임계값 낮춤)
    """
    print("=== 실시간 음성 인식 모드 ===")
    print("종료하려면 'quit' 또는 'exit'를 말씀하세요.")
    print("볼륨 임계값: 100 (작은 소리도 인식)")
    print()
    
    # 현재 스크립트의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # whisper.cpp 경로 설정
    whisper_cli_path = os.path.join(current_dir, "..", "pyannote", "whisper.cpp_local", "whisper-cli")
    model_path = os.path.join(current_dir, "..", "pyannote", "whisper.cpp_local", "model", "ggml-large-v2-q8_0.bin")
    
    # whisper.cpp 실행 파일 존재 확인
    if not os.path.exists(whisper_cli_path):
        print(f"오류: whisper-cli를 찾을 수 없습니다: {whisper_cli_path}")
        return
    
    # 모델 파일 존재 확인
    if not os.path.exists(model_path):
        print(f"오류: 모델 파일을 찾을 수 없습니다: {model_path}")
        return
    
    try:
        while True:
            # 녹음 시간 설정
            duration = 5  # 5초씩 녹음
            
            # 볼륨 체크를 포함한 마이크에서 오디오 녹음 (임계값: 100)
            audio_data = record_audio_with_volume_check(duration=duration, threshold=100)
            
            if audio_data is None:
                print("다시 시도해주세요...")
                continue
            
            # 임시 WAV 파일 생성
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_wav_path = temp_file.name
            
            # 오디오 데이터를 WAV 파일로 저장
            save_audio_to_wav(audio_data, temp_wav_path)
            
            # pydub로 오디오 처리
            print("오디오 전처리 중...")
            audio = AudioSegment.from_wav(temp_wav_path)
            
            # 노이즈 제거 (Low-pass filter 3000Hz)
            audio = audio.low_pass_filter(3000)
            
            # 볼륨 높이기 (+5 dB)
            audio = audio + 5
            
            # 처리된 오디오를 다시 저장
            audio.export(temp_wav_path, format="wav")
            
            # whisper.cpp로 텍스트 변환
            print("텍스트 변환 중...")
            whisper_cmd = [
                whisper_cli_path,
                "-l", "ko",
                "-m", model_path,
                temp_wav_path
            ]
            
            result = subprocess.run(whisper_cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=os.path.dirname(whisper_cli_path))
            
            # 임시 파일 삭제
            os.unlink(temp_wav_path)
            
            if result.returncode == 0:
                transcribed_text = result.stdout.strip()
                if transcribed_text:
                    print(f"🎯 인식 결과: {transcribed_text}")
                    
                    # 종료 명령 확인
                    if transcribed_text.lower() in ['quit', 'exit', '종료', '끝']:
                        print("실시간 음성 인식을 종료합니다.")
                        break
                else:
                    print("음성이 인식되지 않았습니다.")
            else:
                print("❌ 텍스트 변환 실패")
            
            print("-" * 50)
            
    except KeyboardInterrupt:
        print("\n실시간 음성 인식을 종료합니다.")
    except Exception as e:
        print(f"오류 발생: {e}")

def is_audio_loud_enough(audio_data, threshold=100):  # 1000 → 100으로 낮춤
    """
    오디오 볼륨이 충분한지 확인 (임계값을 낮춤)
    
    Args:
        audio_data (numpy.ndarray): 오디오 데이터
        threshold (int): 볼륨 임계값 (기본값: 100)
    
    Returns:
        bool: 볼륨이 충분한지 여부
    """
    rms = np.sqrt(np.mean(audio_data**2))
    print(f"현재 볼륨 레벨: {rms:.2f} (임계값: {threshold})")
    return rms > threshold

def record_audio_with_volume_check(duration=5, sample_rate=16000, threshold=100):
    """
    볼륨 체크를 포함한 오디오 녹음 (임계값을 낮춤)
    
    Args:
        duration (int): 녹음 시간 (초)
        sample_rate (int): 샘플링 레이트
        threshold (int): 볼륨 임계값 (기본값: 100)
    
    Returns:
        numpy.ndarray or None: 녹음된 오디오 데이터 또는 None
    """
    print(f"🎤 {duration}초 동안 녹음 중... (말씀해주세요)")
    
    audio_data = sd.rec(int(duration * sample_rate), 
                       samplerate=sample_rate, 
                       channels=1, 
                       dtype='int16')
    sd.wait()
    
    if is_audio_loud_enough(audio_data, threshold):
        print("✅ 충분한 볼륨 감지됨!")
        return audio_data
    else:
        print("⚠️ 볼륨이 낮지만 계속 진행합니다...")
        return audio_data  # None 대신 audio_data 반환 (계속 진행)

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='whisper.cpp를 사용한 오디오 텍스트 변환')
    parser.add_argument('input_file', nargs='?', help='변환할 오디오 파일 경로')
    parser.add_argument('-o', '--output', help='출력 디렉토리 (기본값: 입력 파일과 같은 디렉토리)')
    parser.add_argument('--realtime', action='store_true', help='실시간 마이크 입력 모드')
    parser.add_argument('--threshold', type=int, default=100, help='볼륨 임계값 (기본값: 100)')
    
    args = parser.parse_args()
    
    # 실시간 모드가 요청된 경우
    if args.realtime:
        process_realtime_audio()
        return
    
    # 입력 파일이 제공된 경우 파일 처리
    if args.input_file:
        result_file = process_audio_file(args.input_file, args.output)
        if result_file:
            print(f"\n✅ 변환 성공! 결과 파일: {result_file}")
        else:
            print("\n❌ 변환 실패!")
        return
    
    # 대화형 모드
    print("=== whisper.cpp 오디오 텍스트 변환 프로그램 ===")
    print("1. 파일 변환 모드")
    print("2. 실시간 음성 인식 모드")
    print("3. 종료")
    print()
    
    while True:
        choice = input("모드를 선택하세요 (1-3): ").strip()
        
        if choice == "1":
            # 파일 변환 모드
            input_file = input("변환할 오디오 파일 경로를 입력하세요: ").strip()
            if input_file:
                output_dir = input("출력 디렉토리를 입력하세요 (엔터시 기본값): ").strip()
                if not output_dir:
                    output_dir = None
                
                result_file = process_audio_file(input_file, output_dir)
                
                if result_file:
                    print(f"\n✅ 변환 성공! 결과 파일: {result_file}")
                else:
                    print("\n❌ 변환 실패!")
            break
            
        elif choice == "2":
            # 실시간 음성 인식 모드
            process_realtime_audio()
            break
            
        elif choice == "3":
            print("프로그램을 종료합니다.")
            break
            
        else:
            print("잘못된 선택입니다. 1, 2, 또는 3을 입력하세요.")

if __name__ == "__main__":
    main()