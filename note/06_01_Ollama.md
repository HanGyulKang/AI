## Ollama
- **정의**
  - 로컬 PC에서 실행
  - 반드시 `GGUF` 확장자를 가진 파일이 있어야 구동이 가능하다
- **활용**
  - `ollama pull {model 명}` : 모델 설치
  - `ollama run {model 명}` : Terminal에서 간단하게 실행
  - `/bye` 로 종료
  - 다운받은 `GGUF` 파일 실행
    - `ModelFile` 파일 작성 필수
    - `ollama create {custom model name} -f /{path}/ModelFile`로 다운받은 모델 생성

```text
# ModelFile
FROM {fileName}.gguf

{LLM이 요구하는 Prompt Template}
```

#### GGUF
- **정의**
  - **LLM**을 저장하는데 사용되는 파일 형식
- **활용**
  - **LLM**을 다운받아서 사용하려면 매우 많고 다양한 파일들을 받아야했지만, `GGUF`가 나온 이후 단일 파일로 간편하게 받아볼 수 있음
  - `GGML` 모델은 `GPU`가 아닌 `CPU`에서 실행할 수 있어서 접근성이 용이함

```python
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_teddynote.messages import stream_response

llm = ChatOllama(model="{ollama에 등록한 모델명}") # ollama로 생성한 모델 생성
prompt = ChatPromptTemplate.from_template("{num1} + {num2}는?") 

chain = prompt | llm | StrOutputParser() # Chain 생성

answer = chain.stream({"num1": 3, "num2": 5})
stream_response(answer)
```
