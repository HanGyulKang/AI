# https://huggingface.co/pyannote/speaker-diarization-3.1

from pyannote.audio import Pipeline
import os
from dotenv import load_dotenv
import torchaudio
import torch

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
audio_file = os.path.join(current_dir, "test.audio", "test3.mp3")

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
    
    # 임시 WAV 파일로 저장 (pyannote가 더 안정적으로 처리)
    temp_wav_file = os.path.join(current_dir, "temp_audio.wav")
    torchaudio.save(temp_wav_file, waveform, target_sample_rate)
    print(f"임시 WAV 파일 생성: {temp_wav_file}")
    
    # 화자 분리 실행
    diarization = pipeline(temp_wav_file)
    
    print("\n=== 화자 분리 결과 ===")
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"Speaker {speaker} from {turn.start:.2f}s to {turn.end:.2f}s")
    
    # 임시 파일 삭제
    os.remove(temp_wav_file)
    print(f"임시 파일 삭제 완료")
        
except Exception as e:
    print(f"화자 분리 처리 중 오류 발생: {e}")
    # 임시 파일이 있다면 삭제
    temp_wav_file = os.path.join(current_dir, "temp_audio.wav")
    if os.path.exists(temp_wav_file):
        os.remove(temp_wav_file)