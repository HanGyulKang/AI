import os
from pydub import AudioSegment
from faster_whisper import WhisperModel # offline에서 가능

def convert_audio_to_text_offline(audio_file_path):
    """
    오프라인에서 오디오 파일을 텍스트로 변환하는 함수 (Faster Whisper 사용)
    """
    # 오디오 파일 확장자 확인
    file_extension = os.path.splitext(audio_file_path)[1].lower()
    
    # 임시 WAV 파일 경로
    temp_wav_path = "/tmp/temp_audio.wav"
    
    try:
        # MP3 또는 WebM 파일을 WAV로 변환
        if file_extension in ['.mp3', '.webm']:
            audio = AudioSegment.from_file(audio_file_path)
            audio.export(temp_wav_path, format="wav")
        else:
            print(f"지원하지 않는 파일 형식입니다: {file_extension}")
            return None
        
        # Faster Whisper 모델 로드 (오프라인)
        # 'base' 모델은 작고 빠르지만, 'medium' 또는 'large' 모델이 더 정확합니다
        model = WhisperModel("base", device="cpu", compute_type="int8")
        
        # 음성 인식 실행
        segments, info = model.transcribe(temp_wav_path, language="ko")
        
        # 결과 텍스트 수집
        text = ""
        for segment in segments:
            text += segment.text + " "
        
        # 임시 파일 삭제
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        
        return text.strip()
        
    except Exception as e:
        print(f"음성 인식 중 오류 발생: {str(e)}")
        # 임시 파일 정리
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        return None

def main():
    # 입력 파일 경로
    input_file = "/Users/gooroomee/Downloads/bgmTest.mp3"
    
    # 출력 폴더 생성
    output_dir = "/Users/gooroomee/Downloads/audioToText"
    os.makedirs(output_dir, exist_ok=True)
    
    # 출력 파일 경로
    output_file = os.path.join(output_dir, "transcribed_text_offline.txt")
    
    print("오프라인 음성 인식으로 텍스트 변환 중...")
    
    # 음성 인식으로 텍스트 변환
    transcribed_text = convert_audio_to_text_offline(input_file)
    
    if transcribed_text is None:
        print("음성 인식에 실패했습니다.")
        return
    
    print(f"음성 인식 결과: {transcribed_text}")
    
    # 결과를 파일로 저장
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== 오프라인 음성 인식 결과 ===\n")
            f.write("(Faster Whisper 모델 사용)\n\n")
            f.write("=== 변환된 텍스트 ===\n")
            f.write(transcribed_text)
        
        print(f"텍스트 변환이 완료되었습니다!")
        print(f"저장 위치: {output_file}")
        
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 