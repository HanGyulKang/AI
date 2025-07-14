from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 단계 1: 문서 로드(Load Documents)
loader = PyMuPDFLoader("data/내월급.pdf")
docs = loader.load()

# 단계 2: 문서 분할(Split Documents)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
split_documents = text_splitter.split_documents(docs)

# 단계 3: 임베딩(Embedding) 생성
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 단계 4: DB 생성(Create DB) 및 저장 : 택1
# >> FAISS 벡터 스토어
vectorstore = FAISS.from_documents(documents=split_documents, embedding=embeddings)

# >> 또는 Chroma 벡터 스토어
vectorstore = Chroma.from_documents(
    documents=split_documents, 
    embedding=embeddings,
    persist_directory="./chroma_db"  # 영구 저장 디렉토리 추가
)

# 단계 5: 검색기(Retriever) 생성
# 문서에 포함되어 있는 정보를 검색하고 생성합니다.
retriever = vectorstore.as_retriever()

# 단계 6: 프롬프트 생성(Create Prompt)
# 프롬프트를 생성합니다.
prompt = PromptTemplate.from_template(
    """너는 월급 절약에 탁월한 자린고비야.
    내가 받은 월급을 보고 한달 동안 하루에 얼마를 써도 되는지 알려줘.

#Context: 
{context}

#Question:
{question}

#Answer:"""
)

# 단계 7: 언어모델(LLM) 생성
# 모델(LLM) 을 생성합니다.
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

# 단계 8: 체인(Chain) 생성
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

response = chain.invoke("저번 달에는 월급 중에 102%를 사용했어. 이제 어떻게 살아야할까?")
print(response)