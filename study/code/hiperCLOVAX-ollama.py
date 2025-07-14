# [실행 방법]
# 1. models/hyperCLOVAX 디렉토리에서
# cd models/hyperCLOVAX
# 2. 모델 생성
# ollama create {custom_model_name} -f Modelfile
# 모델 실행
# ollama run {custom_model_name}

from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

def stream_response(response_stream):
    """스트리밍 응답을 출력하는 함수"""
    full_response = ""
    for chunk in response_stream:
        if chunk:
            print(chunk, end="", flush=True)
            full_response += chunk
    print()  # 마지막에 줄바꿈
    return full_response

llm = ChatOllama(model="hyperclovax") # ollama로 생성한 모델 생성

# Modelfile의 Template에 맞춘 ChatPromptTemplate 생성
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 날짜의 신입니다. 어떤 날짜를 물어봐도 정확한 날짜를 알려주지요."),
    ("user", "오늘은 2025년 7월 3일이야. 오늘로부터 {Prompt}일 뒤의 날짜는?"),
    ("assistant", "")
])

chain = prompt | llm | StrOutputParser() # Chain 생성

answer = chain.stream({"Prompt": 30})
stream_response(answer)

