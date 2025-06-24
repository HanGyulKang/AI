import os
import speech_recognition as sr # online 필수
from pydub import AudioSegment

def convert_audio_to_text(audio_file_path):
    """
    오디오 파일을 텍스트로 변환하는 함수
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
        
        # 음성 인식기 초기화
        recognizer = sr.Recognizer()
        
        # 오디오 파일 로드
        with sr.AudioFile(temp_wav_path) as source:
            # 노이즈 제거
            recognizer.adjust_for_ambient_noise(source)
            # 오디오 데이터 추출
            audio_data = recognizer.record(source)
        
        # Google Speech Recognition을 사용하여 텍스트 변환
        text = recognizer.recognize_google(audio_data, language='ko-KR')
        
        # 임시 파일 삭제
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        
        return text
        
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
    output_file = os.path.join(output_dir, "transcribed_text.txt")
    
    print("음성 파일을 텍스트로 변환 중...")
    print("(Google Speech Recognition API 사용)")
    
    # 음성 인식으로 텍스트 변환
    transcribed_text = convert_audio_to_text(input_file)
    
    if transcribed_text is None:
        print("음성 인식에 실패했습니다.")
        return
    
    print(f"음성 인식 결과: {transcribed_text}")
    
    # 결과를 파일로 저장
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== 온라인 음성 인식 결과 ===\n")
            f.write("(Google Speech Recognition API 사용)\n\n")
            f.write("=== 변환된 텍스트 ===\n")
            f.write(transcribed_text)
        
        print(f"텍스트 변환이 완료되었습니다!")
        print(f"저장 위치: {output_file}")
        
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()