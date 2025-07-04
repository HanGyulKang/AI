# VectorStoreRetrieverMemory

---

**시간 순서 고려 없이** 과거 대화 내용 중 가장 눈에 띄는 상위 K개의 문서를 **쿼리**한다.

### 필수 요소
1. Vector Store
2. Embedding Model

### 사용 방법

#### 초기화
````python
import faiss
from langchain_openai import OpenAIEmbeddings
from langchain.docstore import InMemoryDocstore
from langchain.vectorstores import FAISS

# 임베딩 모델 초기화
embeddings_model = OpenAIEmbeddings()
embedding_size = 1536

# Vector store DB 초기화
index = faiss.IndexFlatL2(embedding_size)

# 초기화 완료
vectorstore = FAISS(embeddings_model, index, InMemoryDocstore({}), {})
````

#### Vector Store 설정
```python
from langchain.memory import VectorStoreRetrieverMemory

# 검색기 초기화
# as_retriever로 검색기 부착
# search_kwargs : 과거 대화 기록 k개 설정
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
memory = VectorStoreRetrieverMemory(retriever=retriever)
```

#### 저장
```python
memory.save_context(
    inputs={
        "human": "some blabla"
    },
    outputs={
        "ai": "some answer"
    }
)
```

#### 추출
```python
query = {
    "human": "{질의 내용}"
}
memory.load_memory_variables({query})["history"]
```

위 예제처럼 과거 대화 내용중에 `query`내용과 가장 유사한 정보를 추출해낸다.  
마치 AI에게 질의하는 것과 비슷하다.  

#### 장점
질의를 통해서 관련된 내용을 추출할 수 있기 때문에 오래 된 대화 내용이 많이 누적됐을 때 강력하다.