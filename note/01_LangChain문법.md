## 프롬프트 캐싱
- **정의**: 동일한 프롬프트에 대한 응답을 저장해두고 재사용하는 기능
- **장점**:
  * API 호출 비용 절감
  * 응답 속도 향상
  * 동일한 질문에 대한 일관된 답변 보장
- **사용 예시**:
  ```python
  from langchain.cache import InMemoryCache
  from langchain.globals import set_llm_cache
  
  # 메모리에 캐시 저장
  set_llm_cache(InMemoryCache())
  
  # 또는 Redis를 사용한 캐싱
  from langchain.cache import RedisCache
  set_llm_cache(RedisCache(redis_url="redis://localhost:6379"))
  ```

## 멀티모달
- **정의**: 텍스트, 이미지, 오디오 등 다양한 형태의 데이터를 함께 처리하는 기능
- **주요 기능**:
  * 이미지 분석 및 설명
  * 이미지 기반 질의응답
  * 이미지 생성
  * 오디오-텍스트 변환
- **사용 예시**:
  ```python
  from langchain.llms import OpenAI
  from langchain.chains import LLMChain
  from langchain.prompts import PromptTemplate
  
  # 이미지 분석
  def analyze_image(image_path):
      # 이미지를 텍스트로 변환
      image_to_text = ImageToText()
      text = image_to_text.convert(image_path)
      
      # 변환된 텍스트로 질의응답
      llm = OpenAI()
      chain = LLMChain(llm=llm, prompt=PromptTemplate(...))
      return chain.run(text)
  ```

## Prompt
- **정의**: AI 모델과의 대화를 구조화하는 프롬프트 템플릿
- **구성 요소**:
  * **System Prompt**: AI의 역할과 행동 지침을 정의. 고정된 전역 상수처럼 활용
  * **User Prompt**: 사용자의 실제 질문이나 요청. 사용자 정의 프롬프트로 변수와 비슷
  * **Assistant Prompt**: AI의 응답 형식 정의
- **사용 예시**:
  ```python
  from langchain.prompts import PromptTemplate
  
  # 프롬프트 템플릿 생성
  template = PromptTemplate.from_messages([
      ("system", "당신은 친절한 AI 비서입니다."),
      ("user", "{input}"),
      ("assistant", "네, 이해했습니다. {input}에 대해 답변드리겠습니다.")
  ])
  
  # 프롬프트 사용
  messages = template.format_messages(input="파이썬이란 무엇인가요?")
  ```


## LCEL(LangChain Expression Language)
- **정의**: LangChain의 구성 요소들을 파이프라인 형태로 쉽게 결합할 수 있는 표현 언어
- **주요 특징**:
  * 파이프라인 구성 요소를 `|` 연산자로 연결
  * 비동기 처리 지원 (`arun`, `ainvoke` 등)
  * 스트리밍 지원 (`astream`, `stream` 등)
  * 재사용 가능한 컴포넌트 생성
- **기본 구성 요소**:
  * **Prompt**: 사용자 입력을 받아 프롬프트 생성
  * **Model**: LLM 모델 호출
  * **Output Parser**: 모델 출력을 원하는 형식으로 변환
  * **Retriever**: 관련 문서 검색
  * **Memory**: 대화 기록 저장
- **사용 예시**:
  ```python
  from langchain.prompts import PromptTemplate
  from langchain.chat_models import ChatOpenAI
  from langchain.schema import StrOutputParser
  
  # 기본적인 체인 구성
  prompt = PromptTemplate.from_template("다음 질문에 답변해주세요: {question}")
  model = ChatOpenAI(model="gpt-4.1-nano", temperature=0.1)
  output_parser = StrOutputParser()
  
  # 파이프라인 구성
  chain = prompt | model | output_parser
  
  # 실행
  result = chain.invoke({"question": "파이썬이란 무엇인가요?"})
  
  # 비동기 실행
  async def run_chain():
      result = await chain.ainvoke({"question": "파이썬이란 무엇인가요?"})
      return result
  ```

## LCEL 인터페이스
- **정의**: LangChain의 모든 구성 요소가 구현하는 표준화된 인터페이스
- **Runnable 프로토콜**:
  * 모든 LangChain 구성 요소의 기본 인터페이스
  * 동기/비동기 작업을 일관된 방식으로 처리
  * 스트리밍, 배치 처리 등 다양한 실행 모드 지원

- **실행 모드**:
  * **동기(Sync) 실행**:
    - `invoke`: 단일 입력에 대한 실행
    - `stream`: 응답을 청크 단위로 스트리밍
    - `batch`: 여러 입력을 한 번에 처리
  * **비동기(Async) 실행**:
    - `ainvoke`: 비동기 단일 실행
    - `astream`: 비동기 스트리밍
    - `abatch`: 비동기 배치 처리
    - `astream_log`: 중간 단계와 최종 결과를 모두 스트리밍

- **사용 예시**:
  ```python
  from langchain.prompts import PromptTemplate
  from langchain.chat_models import ChatOpenAI
  from langchain.schema import StrOutputParser
  
  # 기본 체인 구성
  chain = (
      PromptTemplate.from_template("다음 질문에 답변해주세요: {question}")
      | ChatOpenAI()
      | StrOutputParser()
  )
  
  # 동기 실행
  result = chain.invoke({"question": "파이썬이란?"})
  
  # 스트리밍
  for chunk in chain.stream({"question": "파이썬이란?"}):
      print(chunk)
  
  # 배치 처리
  results = chain.batch([
      {"question": "파이썬이란?"},
      {"question": "자바란?"}
  ])
  
  # 비동기 실행
  async def run_async():
      result = await chain.ainvoke({"question": "파이썬이란?"})
      return result
  ```

### Parallel : 병렬 처리
- **정의**: 여러 체인을 동시에 실행하고 결과를 조합하는 기능
- **주요 특징**:
  * 독립적인 체인들을 병렬로 실행
  * 결과를 딕셔너리 형태로 조합
  * 각 체인의 실행 결과를 키로 구분
  * 에러 발생 시 개별 체인만 실패

- **사용 예시**:
  ```python
  from langchain_core.runnables import RunnableParallel
  from langchain.prompts import PromptTemplate
  from langchain.chat_models import ChatOpenAI
  from langchain.schema import StrOutputParser
  
  # 덧셈 체인
  chain1 = (
      PromptTemplate.from_template("{num1}과 {num2}의 합은?")
      | ChatOpenAI()
      | StrOutputParser()
  )
  
  # 곱셈 체인
  chain2 = (
      PromptTemplate.from_template("{num1}과 {num2}의 곱은?")
      | ChatOpenAI()
      | StrOutputParser()
  )
  
  # 병렬 실행 구성
  combined = RunnableParallel(
      plus=chain1,    # 결과는 'plus' 키로 접근
      multiply=chain2 # 결과는 'multiply' 키로 접근
  )
  
  # 실행
  result = combined.invoke({"num1": "3", "num2": "4"})
  # 결과: {'plus': '7', 'multiply': '12'}
  
  # 비동기 실행
  async def run_parallel():
      result = await combined.ainvoke({"num1": "3", "num2": "4"})
      return result
  ```

- **장점**:
  * 성능 향상: 독립적인 작업을 동시에 처리
  * 코드 모듈화: 각 체인을 독립적으로 관리
  * 유연한 결과 처리: 키를 통한 명확한 결과 구분
  * 에러 격리: 한 체인의 실패가 다른 체인에 영향을 주지 않음

## Output Parser(출력 파서)
- **정의**: LLM의 출력을 구조화된 형식으로 변환하는 도구
- **주요 기능**:
  * JSON, CSV 등 특정 형식으로 출력 변환
  * 출력 데이터의 유효성 검증
  * 에러 처리 및 예외 상황 관리
- **종류**:
  * **StrOutputParser**: 문자열 출력
  * **PydanticOutputParser**: Pydantic 모델 기반 구조화
  * **CommaSeparatedListOutputParser**: 쉼표로 구분된 리스트
  * **StructuredOutputParser**: 사용자 정의 구조
- **사용 예시**:
  ```python
  from langchain.output_parsers import PydanticOutputParser
  from pydantic import BaseModel, Field
  from typing import List
  
  # 출력 구조 정의
  class Answer(BaseModel):
      answer: str = Field(description="질문에 대한 답변")
      confidence: float = Field(description="답변의 신뢰도")
      sources: List[str] = Field(description="참고한 출처들")
  
  # 파서 설정
  parser = PydanticOutputParser(pydantic_object=Answer)
  
  # 프롬프트에 파서 형식 추가
  prompt = PromptTemplate.from_template(
      "다음 질문에 답변해주세요: {question}\n{format_instructions}"
  )
  
  # 체인 구성
  chain = prompt | model | parser
  
  # 실행
  result = chain.invoke({
      "question": "파이썬이란 무엇인가요?",
      "format_instructions": parser.get_format_instructions()
  })
  ```