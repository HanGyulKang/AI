from langchain_ollama import ChatOllama
from langchain_community.memory.kg import ConversationKGMemory
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationChain

llm = ChatOllama(model="EEVE-Korean-10.8B:latest", temperature=0)

template = """다음은 인간과 AI 간의 친근한 대화입니다.
AI는 수다스럽고 컨텍스트에서 구체적인 세부사항을 많이 제공합니다.
AI가 질문에 대한 답을 모르는 경우, 솔직하게 모른다고 말합니다.
AI는 "관련 정보" 섹션에 포함된 정보만 사용하며 환각을 일으키지 않습니다.

관련 정보:

{history}

대화:
인간: {input}
AI:"""

prompt = PromptTemplate(
    input_variables=["history", "input"], template=template)

conversation_with_kg = ConversationChain(
    llm=llm, prompt=prompt, memory=ConversationKGMemory(llm=llm)
)

conversation_with_kg.predict(
    input="여기는 장유라입니다."
    "장유라씨는 개발자입니다."
    "그녀는 2년전에 결혼했고 해외 여행 갈 계획을 세우고있어."
)

print(conversation_with_kg.memory.load_memory_variables({"input": "장유라씨는 누구시죠?"}))