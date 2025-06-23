import os
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from langchain_huggingface import HuggingFaceEndpoint
import librosa
importsoundfile as sf

class KoreanSpeechToText:
    def __init__(self, model_name="openai/whisper-large-v3", use_endpoint=False, endpoint_url=None):
        """
        한국어 음성 인식 클래스
        
        Args:
            model_name: 사용할 모델명
            use_endpoint: Dedicated Endpoint 사용 여부
            endpoint_url: Endpoint URL (use_endpoint=True일 때)
        """
        self.model_name = model_name
        self.use_endpoint = use_endpoint
        
        if use_endpoint:
            # Dedicated Endpoint 사용
            self.llm = HuggingFaceEndpoint(
                endpoint_url=endpoint_url,
                task="automatic-speech-recognition",
                huggingfacehub_api_token=os.environ.get("HUGGINGFACEHUB_API_TOKEN")
            )
        else:
            # 로컬 모델 사용
            self.processor = WhisperProcessor.from_pretrained(model_name)
            self.model = WhisperForConditionalGeneration.from_pretrained(model_name)
            
            # 한국어 설정
            self.processor.tokenizer.set_prefix_tokens(language="ko", task="transcribe")
    
    def transcribe_audio(self, audio_path):
        """
        오디오 파일을 텍스트로 변환
        
        Args:
            audio_path: 오디오 파일 경로 (.mp3, .webm, .wav 등)
        
        Returns:
            str: 변환된 텍스트
        """
        if self.use_endpoint:
            # Endpoint 사용 시
            with open(audio_path, "rb") as audio_file:
                result = self.llm.invoke(audio_file.read())
            return result
        else:
            # 로컬 모델 사용 시
            # 오디오 로드 및 전처리
            audio, sample_rate = librosa.load(audio_path, sr=16000)
            
            # Whisper 입력 형식으로 변환
            input_features = self.processor(
                audio, 
                sampling_rate=16000, 
                return_tensors="pt"
            ).input_features
            
            # 한국어 설정
            forced_decoder_ids = self.processor.get_decoder_prompt_ids(
                language="ko", 
                task="transcribe"
            )
            
            # 추론
            with torch.no_grad():
                predicted_ids = self.model.generate(
                    input_features,
                    forced_decoder_ids=forced_decoder_ids,
                    max_length=448
                )
            
            # 텍스트 디코딩
            transcription = self.processor.batch_decode(
                predicted_ids, 
                skip_special_tokens=True
            )[0]
            
            return transcription

# 사용 예시
if __name__ == "__main__":
    # 환경 변수 설정 (필요시)
    # os.environ["HUGGINGFACEHUB_API_TOKEN"] = "your_token_here"
    
    # 1. 로컬 모델 사용
    stt_local = KoreanSpeechToText(model_name="openai/whisper-large-v3")
    
    # 2. Dedicated Endpoint 사용
    # stt_endpoint = KoreanSpeechToText(
    #     model_name="openai/whisper-large-v3",
    #     use_endpoint=True,
    #     endpoint_url="your_endpoint_url_here"
    # )
    
    # 음성 파일 변환
    audio_file = "path/to/your/audio.mp3"
    if os.path.exists(audio_file):
        result = stt_local.transcribe_audio(audio_file)
        print(f"변환 결과: {result}")
    else:
        print("오디오 파일을 찾을 수 없습니다.") 