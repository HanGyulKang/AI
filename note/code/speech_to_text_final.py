import os
from pydub import AudioSegment
from pydub.effects import normalize
from faster_whisper import WhisperModel
from datetime import datetime
import torch

# 전역 변수로 모델 저장 (재사용을 위해)
_whisper_model = None
_model_loaded = False

def get_whisper_model():
    """
    Whisper 모델을 싱글톤으로 관리하는 함수 (오프라인 지원)
    """
    global _whisper_model, _model_loaded
    
    if not _model_loaded:
        print("음성 인식 모델 로딩 중...")
        
        # GPU 사용 가능 여부 확인
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        # 오프라인 모드로 시도 (캐시된 모델 사용)
        try:
            print("로컬 캐시에서 모델 로딩 시도 중...")
            _whisper_model = WhisperModel(
                "large-v2", 
                device=device, 
                compute_type=compute_type,
                local_files_only=True  # 오프라인 모드 강제
            )
            print("✓ 오프라인 모드로 모델 로딩 성공!")
        except Exception as e:
            print(f"로컬 모델을 찾을 수 없습니다: {e}")
            print("인터넷 연결이 필요합니다. 모델을 다운로드합니다...")
            _whisper_model = WhisperModel(
                "large-v2", 
                device=device, 
                compute_type=compute_type,
                local_files_only=False  # 온라인 다운로드 허용
            )
            print("✓ 모델 다운로드 완료! 다음 실행부터는 오프라인에서 사용 가능합니다.")
        
        _model_loaded = True
        print(f"모델 로딩 완료! (Device: {device}, Compute Type: {compute_type})")
    else:
        print("기존 모델 재사용 중...")
    
    return _whisper_model

def preprocess_audio(audio):
    """
    오디오 전처리 함수 (whisper.cpp 최적화)
    """
    # 스테레오를 모노로 변환 (음성 인식에 더 적합)
    if audio.channels == 2:
        print("스테레오를 모노로 변환 중...")
        audio = audio.set_channels(1)
    
    # 샘플레이트를 16kHz로 변환 (Whisper 모델에 최적화)
    if audio.frame_rate != 16000:
        print(f"샘플레이트를 16kHz로 변환 중... (현재: {audio.frame_rate}Hz)")
        audio = audio.set_frame_rate(16000)
    
    # 오디오 정규화 (볼륨 레벨 조정)
    print("오디오 정규화 중...")
    audio = normalize(audio)
    
    # whisper.cpp 스타일 볼륨 조정 (더 보수적)
    audio = audio + 10  # 10dB 증가 (whisper.cpp 스타일)
    
    return audio

def convert_audio_to_text_improved(audio_file_path):
    """
    개선된 오디오 파일을 텍스트로 변환하는 함수 (whisper.cpp 최적화 적용)
    """
    # 오디오 파일 확장자 확인
    file_extension = os.path.splitext(audio_file_path)[1].lower()
    
    if file_extension not in ['.mp3', '.webm', '.wav', '.m4a', '.flac']:
        print(f"지원하지 않는 파일 형식입니다: {file_extension}")
        return None
    
    # 임시 WAV 파일 경로
    temp_wav_path = "/tmp/temp_audio_whisper_cpp_optimized.wav"
    
    try:
        print("오디오 파일 로딩 중...")
        audio = AudioSegment.from_file(audio_file_path)
        
        # 오디오 정보 출력
        total_duration = len(audio)
        total_minutes = total_duration / 60000
        print(f"원본 오디오 정보:")
        print(f"  - 길이: {total_minutes:.1f}분 ({total_duration/1000:.1f}초)")
        print(f"  - 채널: {audio.channels}개")
        print(f"  - 샘플레이트: {audio.frame_rate}Hz")
        
        # 30분 제한 확인
        if total_minutes > 30:
            print(f"경고: 파일이 30분을 초과 ({total_minutes:.1f}분).")
            audio = audio[:30 * 60 * 1000]  # 30분으로 자르기
        
        # 오디오 전처리
        audio = preprocess_audio(audio)
        
        print("전처리된 오디오 정보:")
        print(f"  - 길이: {len(audio)/1000:.1f}초")
        print(f"  - 채널: {audio.channels}개")
        print(f"  - 샘플레이트: {audio.frame_rate}Hz")
        
        # WAV 파일로 저장 (whisper.cpp 최적화)
        print("WAV 파일로 변환 중...")
        audio.export(temp_wav_path, format="wav", parameters=["-ar", "16000"])
        
        # 모델 가져오기 (재사용)
        model = get_whisper_model()
        
        # whisper.cpp 스타일 최적화된 음성 인식 옵션
        print("음성 인식 실행 중... (whisper.cpp 최적화 적용)")
        segments, info = model.transcribe(
            temp_wav_path, 
            language="ko",
            # 노래 인식을 위한 최적화된 파라미터들
            beam_size=5,  # 더 정확한 인식을 위해 증가
            best_of=5,    # 더 많은 후보 검토
            temperature=0.0,  # 결정적 결과 유지
            condition_on_previous_text=True,  # 이전 텍스트 고려
            initial_prompt="",  # 초기 프롬프트 추가
            word_timestamps=False,  # 단어별 타임스탬프 비활성화
            vad_filter=True,  # VAD 필터 활성화
            vad_parameters=dict(
                min_silence_duration_ms=1000,  # 1초로 증가 (노래 중간 휴식 허용)
                speech_pad_ms=300  # 0.3초로 감소
            ),
            # 노래 인식을 위한 임계값 조정
            compression_ratio_threshold=2.4,  # 압축 비율 임계값
            no_speech_threshold=0.3,  # 무음 임계값 낮춤 (0.6 → 0.3)
            # 반복 패널티 완화
            repetition_penalty=0.8,  # 반복 패널티 완화 (1.0 → 0.8)
            length_penalty=1.0,  # 길이 패널티 유지
            # 추가 옵션
            suppress_tokens=[-1],  # EOT 토큰 억제
            without_timestamps=False,  # 타임스탬프 유지
            max_initial_timestamp=1.0,  # 초기 타임스탬프 최대값
        )
        
        # 결과 텍스트 수집 (whisper.cpp 스타일)
        text = ""
        confidence_scores = []
        segment_count = 0
        
        print("\n=== 세그먼트별 인식 결과 (whisper.cpp 최적화) ===")
        prev_end = 0.0
        for i, segment in enumerate(segments):
            segment_text = segment.text.strip()
            if segment_text:  # 빈 텍스트가 아닌 경우만 추가
                text += segment_text + " "
                segment_count += 1
                
                # 세그먼트 정보 출력
                start_time = segment.start
                end_time = segment.end
                duration = end_time - start_time
                print(f"세그먼트 {i}: {start_time:.1f}s - {end_time:.1f}s ({duration:.1f}s)")
                print(f"  텍스트: {segment_text}")
                
                if hasattr(segment, 'avg_logprob'):
                    confidence_scores.append(segment.avg_logprob)
                    print(f"  신뢰도: {segment.avg_logprob:.3f}")
            
            # 세그먼트 간격이 큰 경우 경고 출력
            if i > 0:
                gap = segment.start - prev_end
                if gap > 5.0:  # 5초 이상 간격
                    print(f"⚠️  세그먼트 간격이 큽니다: {gap:.1f}초 (무음으로 인식된 부분)")
            prev_end = segment.end
        
        # 임시 파일 삭제
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        
        # 신뢰도 점수 계산
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        print(f"\n총 {segment_count}개 세그먼트 인식됨")
        print(f"평균 신뢰도: {avg_confidence:.3f}")
        
        return text.strip()
        
    except Exception as e:
        print(f"음성 인식 중 오류 발생: {str(e)}")
        # 임시 파일 정리
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
        return None

def process_multiple_files(file_paths):
    """
    여러 파일을 순차적으로 처리하는 함수
    """
    results = {}
    
    for i, file_path in enumerate(file_paths, 1):
        print(f"\n=== 파일 {i}/{len(file_paths)} 처리 중 ===")
        print(f"파일: {os.path.basename(file_path)}")
        
        result = convert_audio_to_text_improved(file_path)
        if result:
            results[file_path] = result
            print(f"✓ 파일 {i} 처리 완료")
        else:
            print(f"✗ 파일 {i} 처리 실패")
    
    return results

def main():
    # 단일 파일 처리
    input_file = "/Users/gooroomee/Downloads/testMp3/test9.mp3"
    
    # 출력 폴더 생성
    output_dir = "/Users/gooroomee/Downloads/audioToText"
    os.makedirs(output_dir, exist_ok=True)
    
    # 파일명 생성
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d%H%M%S%f")[:-3]
    output_file = os.path.join(output_dir, f"{timestamp}.txt")
    
    # 음성 인식 실행
    transcribed_text = convert_audio_to_text_improved(input_file)
    
    if transcribed_text is None:
        print("음성 인식에 실패")
        return
    
    if not transcribed_text.strip():
        print("음성 인식 결과가 비어있음")
        return
    
    print(f"\n총 {len(transcribed_text)} 문자")
    
    # 결과를 파일로 저장
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transcribed_text)
        
        print(f"\n텍스트 변환이 완료")
        print(f"저장 위치: {output_file}")
        
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 