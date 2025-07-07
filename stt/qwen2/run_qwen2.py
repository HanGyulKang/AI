# 처음 실행하면 Qwen2 모델 15기가분량 다운로드부터 진행...
# 까먹고 캐시에 있는 모델 삭제 안 하면 영원히 15기가 잡아먹음

import os
import torch
import librosa
from transformers import Qwen2AudioForConditionalGeneration, AutoProcessor

# M1 Pro 맥북을 위한 디바이스 설정
def get_device():
    if torch.backends.mps.is_available():
        return "mps"  # Apple Silicon GPU
    elif torch.cuda.is_available():
        return "cuda"  # NVIDIA GPU
    else:
        return "cpu"  # CPU fallback

device = get_device()
print(f"사용 중인 디바이스: {device}")

# 모델 로드 (M1 Pro 최적화)
processor = AutoProcessor.from_pretrained("Qwen/Qwen2-Audio-7B-Instruct")
model = Qwen2AudioForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2-Audio-7B-Instruct", 
    device_map="auto",
    torch_dtype=torch.float16 if device == "mps" else torch.float32  # MPS에서는 float16 권장
)

# 오디오 파일 경로 설정 (절대 경로로 변환)
script_dir = os.path.dirname(os.path.abspath(__file__))
audio_path = os.path.join(script_dir, "..", "targetFiles", "test9.mp3")

# 오디오 파일 존재 확인
if not os.path.exists(audio_path):
    raise FileNotFoundError(f"오디오 파일을 찾을 수 없습니다: {audio_path}")

print(f"오디오 파일 경로: {audio_path}")

# 오디오 로드
audio, sr = librosa.load(audio_path, sr=processor.feature_extractor.sampling_rate)

# 한국어 음성 인식을 위한 영어 프롬프트 구성
text = "<|im_start|>user\n<|AUDIO|>This is a Korean speech audio file. Please transcribe it in Korean. If there are any foreign words (English, Japanese, Chinese, etc.) mixed in, transcribe them in their original language. For example, English words should be written in English, Japanese words in Japanese. Please provide the transcription in Korean for Korean parts and in the original language for foreign words.<|im_end|>\n<|im_start|>assistant\n"

# 입력 처리 (audios 대신 audio 사용)
inputs = processor(
    text=text, 
    audio=audio, 
    return_tensors="pt", 
    padding=True,
    sampling_rate=processor.feature_extractor.sampling_rate  # sampling_rate 명시적 전달
)

# 디바이스로 이동 - 모든 텐서를 명시적으로 이동
if device == "mps":
    # MPS에서는 모든 텐서를 명시적으로 이동
    for key, value in inputs.items():
        if torch.is_tensor(value):
            inputs[key] = value.to(device)
else:
    # CUDA나 CPU에서는 모든 입력을 이동
    inputs = {k: v.to(device) if torch.is_tensor(v) else v for k, v in inputs.items()}

# 생성
print("음성 인식 및 응답 생성 중...")
with torch.no_grad():
    generate_ids = model.generate(
        **inputs, 
        max_new_tokens=256,
        do_sample=True,
        temperature=0.7,
        pad_token_id=processor.tokenizer.eos_token_id
    )

# 응답 디코딩
generate_ids = generate_ids[:, inputs.input_ids.size(1):]
response = processor.batch_decode(
    generate_ids, 
    skip_special_tokens=True, 
    clean_up_tokenization_spaces=False
)[0]

print(f"모델 응답: {response}")
