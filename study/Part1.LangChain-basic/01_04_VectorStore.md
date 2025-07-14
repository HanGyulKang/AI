
1. **Pinecone**
클라우드 기반의 완전 관리형 Vector Database
사용이 매우 간단하고 확장성이 뛰어남
무료 티어 제공
Python, Node.js 등 다양한 언어 SDK 제공
2. **Milvus**
오픈소스 Vector Database
분산 시스템으로 대규모 데이터 처리 가능
Docker로 쉽게 설치 가능
다양한 프로그래밍 언어 지원
3. **Chroma**
오픈소스 Vector Database
Python 기반으로 사용이 매우 간단
로컬에서 쉽게 시작 가능
LangChain과의 통합이 잘 되어있음
4. **Qdrant**
오픈소스 Vector Database
Rust로 작성되어 성능이 뛰어남
다양한 프로그래밍 언어 지원
클라우드 서비스도 제공
5. **Weaviate**
오픈소스 Vector Database
GraphQL API 제공
스키마 기반의 데이터 모델링 지원
클라우드 서비스도 제공
6. **Redis Stack**
Redis에 Vector Search 기능이 추가된 버전
기존 Redis 사용자들에게 친숙
실시간 데이터 처리에 강점
<br><br>

```Python
# ----------------
# 예시
# ----------------
from chromadb import Client, Settings

# Chroma 클라이언트 생성
client = Client(Settings(
    persist_directory="path/to/persist"
))

# 컬렉션 생성
collection = client.create_collection("my_collection")

# 문서 추가
collection.add(
    documents=["This is a document", "This is another document"],
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    ids=["id1", "id2"]
)

# 검색
results = collection.query(
    query_texts=["This is a query"],
    n_results=2
)
```