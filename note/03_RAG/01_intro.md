## RAG 사용 목적?
- 최신 정보 또는 특정 도메인에 대한 정확한 정보(**Context**)를 기반으로 LLM이 답변할 수 있도록 한다.
  - Hallucination(환각) 증상을 대폭 완화
- 정보, 이를테면 PDF 파일을 통째로 Context로 제공하면 LLM에 **Lost in the Middle**(중간에 길 잃어버림) 문제가 발생할 수 있다.

#### **질의 전 사전 단계**
  - **Document load**
    - 문서 전체를 불러오는 것이 아니라 질문에 대해 필요한 문서 정보만 load해서 Context로 전달한다
    - 문서 전체를 Context로 전달하게 되면 비용 문제가 발생한다
  - **Text split**
    - 필요한 부분의 문서중에서도 Chunk 단위로 문서를 분리한다
    - 효율성 증가
    - 예)
      - `text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)`

      `split_documents = text_splitter.split_documents(docs)`
      - 보편적으로 `RCTS`를 많이 씀.
      - `chunk_overlap은` 단락마다 겹치는 부분을 일정부분 주는 것으로 각 분할 문장이 어색하지 않도록 한다.
  - **Embed**
    - **정의** : 문자 또는 문자열을 숫자로 변환한다. 왜?
    - 유사도 검사를 통해서 필요한 단락을 추출한다
    - 문자열을 숫자 좌표계로 변환 : **Embedding**
      - 실제로는 숫자들의 집합인 **Vector** 표현으로 변환 함
      > [짤 지식] OpenAI의 Embedding은 1536차원을 씀.. 숫자가 1536개..
  - **Vector Store**
    - Embedding 자체도 비용이 발생하기 때문에 질의 때마다 Embedding을 하지 않도록 별도로 저장하는 공간

#### **RunTime 단계**
  - **유저의 질의**
  - **Retrieve** : 검색기
    - 토큰 절약: 어떠한 검색 알고리즘으로 **질의와 연관성 있는 결과**를 Vector DB에 **유사도 검색**을 해서 추출함
      - Cosine similarity
      - Max Marginal Relevance(**MMR**)
    - 유사도 검색을 위해서 **질의 문자 또는 문자열도 역시 Embedding**을 통해 Vector 표현으로 변환 함
      - **Sparse Retriever** : 키워드 검색에 강함
      - **Dense Retriever** : 의미 검색에 강함
  - **Prompt**
    - 검색기를 통해 추출한 결과를 Prompt에 담음
  - **LLM**
    - AI 모델에게 질의

```python
# Chain 생성
chain = (
  {"context": retriever, "question": RunnablePassthrough()}
  | prompt
  | llm
  | ...OutputParser()
)

question = "1+2는 뭐야?"
response = chain.invoke(question)
```