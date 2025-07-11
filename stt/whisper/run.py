# https://huggingface.co/pyannote/speaker-diarization-3.1

from pyannote.audio import Pipeline
import os
from dotenv import load_dotenv
import torchaudio
import torch
import subprocess
from pydub import AudioSegment
from pydub.effects import low_pass_filter

# .env 파일 로드
load_dotenv()

# Hugging Face 토큰 가져오기
hf_token = os.getenv("HUGGINGFACE_PYANNOTE_TOKEN")

print(f"토큰 확인: {hf_token[:10] if hf_token else 'None'}...")

if not hf_token:
    print("Hugging Face 토큰이 필요합니다.")
    print("1. https://huggingface.co/settings/tokens 에서 토큰 생성")
    print("2. 다음 모델들에 대한 접근 권한 받기:")
    print("   - https://huggingface.co/pyannote/speaker-diarization-3.1")
    print("   - https://huggingface.co/pyannote/segmentation-3.0")
    print("   - https://huggingface.co/pyannote/clustering-3.0")
    print("3. stt/pyannote/.env 파일에 HUGGINGFACE_PYANNOTE_TOKEN=your_token_here 추가")
    exit(1)

try:
    # pipeline 로드 시 토큰 사용
    print("모델 로딩 중... (시간이 걸릴 수 있습니다)")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=hf_token)
    print("모델 로딩 완료!")
except Exception as e:
    print(f"모델 로딩 실패: {e}")
    print("\n해결 방법:")
    print("1. 다음 모델들에 대한 접근 권한을 확인하세요:")
    print("   - https://huggingface.co/pyannote/speaker-diarization-3.1")
    print("   - https://huggingface.co/pyannote/segmentation-3.0")
    print("   - https://huggingface.co/pyannote/clustering-3.0")
    print("2. 각 페이지에서 'Accept' 버튼을 클릭하세요")
    print("3. 토큰이 올바른지 확인하세요")
    exit(1)

# 현재 스크립트 파일의 디렉토리를 기준으로 절대 경로 생성
current_dir = os.path.dirname(os.path.abspath(__file__))
audio_file = os.path.join(current_dir, "test.audio", "test9.mp3")

print(f"현재 디렉토리: {current_dir}")
print(f"찾는 파일 경로: {audio_file}")

# 파일 존재 확인
if not os.path.exists(audio_file):
    print(f"오디오 파일을 찾을 수 없습니다: {audio_file}")
    print(f"test.audio 폴더 내용:")
    test_audio_dir = os.path.join(current_dir, "test.audio")
    if os.path.exists(test_audio_dir):
        for file in os.listdir(test_audio_dir):
            print(f"  - {file}")
    else:
        print(f"test.audio 폴더가 존재하지 않습니다: {test_audio_dir}")
    exit(1)

print(f"오디오 파일 처리 중: {audio_file}")

try:
    # 오디오 파일 정보 확인
    waveform, sample_rate = torchaudio.load(audio_file)
    print(f"오디오 정보 - 샘플링 레이트: {sample_rate}Hz, 길이: {waveform.shape[1]} 샘플")
    
    # 모델이 기대하는 샘플링 레이트로 리샘플링 (16kHz)
    target_sample_rate = 16000
    if sample_rate != target_sample_rate:
        print(f"샘플링 레이트를 {target_sample_rate}Hz로 변환 중...")
        resampler = torchaudio.transforms.Resample(sample_rate, target_sample_rate)
        waveform = resampler(waveform)
        print(f"변환 완료 - 새로운 길이: {waveform.shape[1]} 샘플")
    
    # 임시 WAV 파일로 저장 (pydub 처리를 위해)
    temp_wav_file = os.path.join(current_dir, "temp_audio.wav")
    torchaudio.save(temp_wav_file, waveform, target_sample_rate)
    
    # pydub를 사용한 Low-pass filter 적용 (3000Hz) - 노이즈 제거
    print("Low-pass filter 적용 중 (3000Hz)...")
    audio_segment = AudioSegment.from_wav(temp_wav_file)
    filtered_audio = low_pass_filter(audio_segment, 3000)
    print("Low-pass filter 적용 완료")
    
    # 볼륨 증폭 (5dB)
    print("볼륨을 5dB 증폭 중...")
    filtered_audio = filtered_audio + 5
    print("볼륨 증폭 완료")
    
    # 필터링된 오디오를 다시 WAV 파일로 저장
    filtered_audio.export(temp_wav_file, format="wav")
    print(f"필터링된 WAV 파일 저장: {temp_wav_file}")
    
    # 화자 분리 실행
    diarization = pipeline(temp_wav_file)
    
    print("\n=== 화자 분리 결과 ===")
    
    # 출력 디렉토리 설정
    speakers_output_dir = os.path.join(current_dir, "speakers_output")
    speakers_output_text_dir = os.path.join(current_dir, "speakers_output_text")
    
    # 디렉토리가 없으면 생성
    os.makedirs(speakers_output_dir, exist_ok=True)
    os.makedirs(speakers_output_text_dir, exist_ok=True)
    
    # 화자별 오디오 분리 및 저장
    print("\n=== 화자별 오디오 분리 중 ===")
    
    # 모든 발화 세그먼트를 시간 순서대로 저장할 리스트
    all_segments = []
    
    # 화자별 세그먼트를 저장할 딕셔너리 초기화
    speaker_segments = {}
    
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"Speaker {speaker} from {turn.start:.2f}s to {turn.end:.2f}s")
        
        # 화자별 세그먼트 수집
        if speaker not in speaker_segments:
            speaker_segments[speaker] = []
        speaker_segments[speaker].append((turn.start, turn.end))
        
        # 각 세그먼트를 시간 순서대로 저장
        all_segments.append({
            'speaker': speaker,
            'start_time': turn.start,
            'end_time': turn.end,
            'start_sample': int(turn.start * target_sample_rate),
            'end_sample': int(turn.end * target_sample_rate)
        })
    
    # 화자별로 오디오 분리 및 저장
    print("\n=== 화자별 오디오 분리 중 ===")
    
    # 모든 화자의 텍스트를 저장할 딕셔너리
    all_speaker_texts = {}
    
    for speaker, segments in speaker_segments.items():
        print(f"Speaker {speaker} 처리 중...")
        
        # 해당 화자의 모든 세그먼트를 하나의 오디오로 합치기
        speaker_audio = torch.zeros_like(waveform)
        
        for start_time, end_time in segments:
            start_sample = int(start_time * target_sample_rate)
            end_sample = int(end_time * target_sample_rate)
            
            # 오디오 길이를 벗어나지 않도록 조정
            start_sample = max(0, min(start_sample, waveform.shape[1] - 1))
            end_sample = max(start_sample + 1, min(end_sample, waveform.shape[1]))
            
            speaker_audio[:, start_sample:end_sample] = waveform[:, start_sample:end_sample]
        
        # 화자별 오디오 파일 저장
        speaker_file = os.path.join(speakers_output_dir, f"speaker_{speaker}.wav")
        torchaudio.save(speaker_file, speaker_audio, target_sample_rate)
        print(f"  저장됨: {speaker_file}")
        
        # Whisper.cpp로 텍스트 변환
        print(f"  Whisper.cpp로 텍스트 변환 중...")
        whisper_cmd = [
            "./whisper.cpp_local/whisper-cli",
            "-l", "ko",
            "-m", "./whisper.cpp_local/model/ggml-large-v2-q8_0.bin",
            speaker_file
        ]
        
        try:
            result = subprocess.run(whisper_cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=current_dir)
            if result.returncode == 0:
                content = result.stdout.strip()
                # 화자별 전체 텍스트 저장
                all_speaker_texts[speaker] = content
                print(f"  텍스트 변환 완료")
            else:
                print(f"  Whisper.cpp 실행 실패: {result.stderr}")
        except Exception as e:
            print(f"  Whisper.cpp 실행 중 오류: {e}")
    
    # 시간 순서대로 세그먼트 정렬
    all_segments.sort(key=lambda x: x['start_time'])
    
    # 각 세그먼트별로 개별 텍스트 변환
    print("\n=== 세그먼트별 개별 텍스트 변환 중 ===")
    segment_texts = []
    
    for i, segment in enumerate(all_segments):
        speaker = segment['speaker']
        start_time = segment['start_time']
        end_time = segment['end_time']
        
        print(f"세그먼트 {i+1}/{len(all_segments)}: Speaker {speaker} ({start_time:.2f}s - {end_time:.2f}s)")
        
        # 해당 세그먼트의 오디오 추출
        segment_audio = torch.zeros_like(waveform)
        start_sample = segment['start_sample']
        end_sample = segment['end_sample']
        segment_audio[:, start_sample:end_sample] = waveform[:, start_sample:end_sample]
        
        # 세그먼트별 임시 WAV 파일 저장
        temp_segment_file = os.path.join(speakers_output_dir, f"temp_segment_{i}.wav")
        torchaudio.save(temp_segment_file, segment_audio, target_sample_rate)
        
        # Whisper.cpp로 세그먼트별 텍스트 변환
        whisper_cmd = [
            "./whisper.cpp_local/whisper-cli",
            "-l", "ko",
            "-m", "./whisper.cpp_local/model/ggml-large-v2-q8_0.bin",
            temp_segment_file
        ]
        
        try:
            result = subprocess.run(whisper_cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=current_dir)
            if result.returncode == 0:
                segment_text = result.stdout.strip()
                if segment_text:  # 빈 텍스트가 아닌 경우만
                    segment_texts.append({
                        'speaker': speaker,
                        'start_time': start_time,
                        'end_time': end_time,
                        'text': segment_text
                    })
                    print(f"  텍스트: {segment_text}")
            else:
                print(f"  텍스트 변환 실패")
        except Exception as e:
            print(f"  텍스트 변환 중 오류: {e}")
        
        # 임시 파일 삭제
        os.remove(temp_segment_file)
    
    # 시간 순서대로 대화 텍스트 생성
    if segment_texts:
        print("\n=== 시간 순서대로 대화 텍스트 생성 중 ===")
        
        # 현재 시간으로 파일명 생성
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S_%f")[:17]
        conversation_file = os.path.join(speakers_output_text_dir, f"{timestamp}.txt")
        
        with open(conversation_file, 'w', encoding='utf-8') as f:
            f.write("=== 시간 순서별 대화 내용 ===\n\n")
            
            for segment in segment_texts:
                speaker = segment['speaker']
                start_time = segment['start_time']
                end_time = segment['end_time']
                text = segment['text']
                
                f.write(f"Speaker {speaker} ({start_time:.2f}s - {end_time:.2f}s): {text}\n\n")
                print(f"Speaker {speaker}: {text}")
        
        print(f"대화 텍스트 파일 저장 완료: {conversation_file}")
    
    # 임시 파일 삭제
    os.remove(temp_wav_file)
    print(f"\n임시 파일 삭제 완료")
    
    # speakers_output 폴더의 모든 음성 파일 삭제
    print("speakers_output 폴더의 음성 파일들 삭제 중...")
    for file in os.listdir(speakers_output_dir):
        if file.endswith('.wav'):
            file_path = os.path.join(speakers_output_dir, file)
            os.remove(file_path)
            print(f"  삭제됨: {file}")
    
    print(f"화자별 오디오 파일들 삭제 완료")
    print(f"통합 텍스트는 {speakers_output_text_dir} 폴더에 저장되었습니다.")
        
except Exception as e:
    print(f"화자 분리 처리 중 오류 발생: {e}")
    # 임시 파일이 있다면 삭제
    temp_wav_file = os.path.join(current_dir, "temp_audio.wav")
    if os.path.exists(temp_wav_file):
        os.remove(temp_wav_file)