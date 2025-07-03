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

#### Parallel : 병렬 처리
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

## Runnable
- **정의**: LangChain의 모든 구성 요소가 구현하는 기본 인터페이스
- **주요 특징**:
  * 모든 LangChain 구성 요소의 기본 클래스
  * 동기/비동기 실행 지원
  * 스트리밍, 배치 처리 등 다양한 실행 모드 제공
  * 체인 구성의 기본 단위

#### RunnablePassthrough
- **정의**: 입력을 그대로 전달하거나 변환하여 다음 단계로 전달하는 유틸리티
- **주요 기능**:
  * 입력 데이터를 그대로 전달
    * **주의사항**: 
      - 딕셔너리 입력 시 전체 딕셔너리가 전달됨
      - 예: `{'n': 3}` 입력 시 `{'n': 3}` 자체가 전달됨
    * **해결 방법**:
      - `operator.itemgetter` 사용: 특정 키의 값만 추출
      - `RunnablePassthrough.assign()` 사용: 새로운 키로 매핑
      - 람다 함수 사용: 커스텀 변환 로직 적용
  * 입력 데이터를 변환하여 전달
  * 여러 입력을 조합하여 전달
- **사용 예시**:
  ```python
  from langchain_core.runnables import RunnablePassthrough
  from operator import itemgetter
  
  # 1. 기본 사용: 입력을 그대로 전달 (주의 필요)
  chain = RunnablePassthrough() | model
  # 입력: {'n': 3} -> 출력: {'n': 3} (전체 딕셔너리가 전달됨)
  
  # 2. itemgetter 사용: 안전한 값 추출
  chain = itemgetter("n") | model
  # 입력: {'n': 3} -> 출력: 3 (값만 전달됨)
  
  # 3. assign 사용: 새로운 키로 매핑
  chain = (
      RunnablePassthrough.assign(
          value=lambda x: x["n"]
      )
      | model
  )
  # 입력: {'n': 3} -> 출력: {'value': 3}
  
  # 4. 람다 함수 사용: 커스텀 변환
  chain = (
      RunnablePassthrough.assign(
          processed=lambda x: x["n"] * 2
      )
      | model
  )
  # 입력: {'n': 3} -> 출력: {'processed': 6}
  
  # 5. 여러 키 처리
  chain = (
      RunnablePassthrough.assign(
          sum=lambda x: x["a"] + x["b"],
          product=lambda x: x["a"] * x["b"]
      )
      | model
  )
  # 입력: {'a': 3, 'b': 4} -> 출력: {'sum': 7, 'product': 12}
  ```

- **일반적인 사용 패턴**:
  * 단일 값 추출: `itemgetter` 사용
  * 값 변환: `assign`과 람다 함수 사용
  * 여러 값 조합: `assign`에 여러 람다 함수 사용
  * 복잡한 변환: 커스텀 함수와 `RunnableLambda` 사용

- **에러 방지 팁**:
  * 항상 입력 데이터의 구조를 확인
  * 필요한 값만 추출하여 사용
  * 타입 힌팅을 통한 타입 안전성 확보
  * 예외 처리 로직 추가

#### RunnableParallel
- **정의**: 여러 체인을 병렬로 실행하고 결과를 조합하는 유틸리티
- **주요 기능**:
  * 독립적인 체인들을 동시에 실행
  * 결과를 딕셔너리 형태로 조합
  * 각 체인의 결과를 키로 구분
- **사용 예시**:
  ```python
  from langchain_core.runnables import RunnableParallel
  
  # 여러 체인을 병렬로 실행
  parallel_chain = RunnableParallel(
      chain1=chain1,
      chain2=chain2,
      chain3=chain3
  )
  
  # 결과는 딕셔너리 형태로 반환
  result = parallel_chain.invoke({"input": "test"})
  # 결과: {'chain1': result1, 'chain2': result2, 'chain3': result3}
  ```

#### RunnableLambda
- **정의**: 사용자 정의 함수를 LangChain 체인에 통합하는 유틸리티
- **주요 기능**:
  * 사용자 정의 함수를 체인에 포함
  * 입력 데이터 변환 및 처리
  * 커스텀 로직 구현
- **주의사항**:
  * 함수는 반드시 파라미터를 가져야 함, 파라미터는 **하나만** 가질 수 있기 떄문에 다중 파라미터를 원한다면
  map에 담아서 넘겨서 key 값으로 꺼내서 다중 파라미터를 가진 함수를 호출하면 됨
  * 입력/출력 타입이 명확해야 함
  * 비동기 함수도 지원
- **사용 예시**:
  ```python
  from langchain_core.runnables import RunnableLambda
  
  # 기본 사용
  def add_one(x: int) -> int:
      return x + 1
  
  chain = RunnableLambda(add_one) | model
  
  # 여러 파라미터 사용
  def combine_inputs(data: dict) -> str:
      return f"{data['question']} {data['context']}"
  
  chain = RunnableLambda(combine_inputs) | model
  
  # 비동기 함수 사용
  async def async_process(data: dict) -> str:
      # 비동기 처리 로직
      return processed_data
  
  chain = RunnableLambda(async_process) | model
  ```

### Runnable 사용 시 주의사항
1. **타입 힌팅**:
   * 입력과 출력의 타입을 명확히 지정
   * 타입 검사를 통한 오류 방지

2. **에러 처리**:
   * 각 단계에서 발생할 수 있는 예외 처리
   * 적절한 에러 메시지 제공

3. **성능 최적화**:
   * 불필요한 변환 최소화
   * 적절한 배치 처리 활용

4. **테스트**:
   * 각 Runnable 컴포넌트의 독립적 테스트
   * 전체 체인의 통합 테스트