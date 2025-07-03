from langchain_ollama import ChatOllama
from langchain.chains import ConversationChain
from langchain.memory import ConversationEntityMemory
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE

llm = ChatOllama(model="llava:7b", temperature=0)

conversation = ConversationChain(
    llm=llm,
    prompt=ENTITY_MEMORY_CONVERSATION_TEMPLATE,
    memory=ConversationEntityMemory(llm=llm),
)

conversation.predict(
    input="한결과 유라는 서로 부부야."
    "한결은 개발자이고 유라도 개발자야. "
    "그들은 2년전에 결혼했고 해외 여행 갈 계획을 세우고있어."
)

print(conversation.memory.entity_store.store) # 특정 Entity에 대한 정보를 저장하고있음