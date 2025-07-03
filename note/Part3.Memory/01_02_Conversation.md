# ConversationBufferMemory

---

* 메시지를 저장한 다음 변수에 메시지를 추출할 수 있게 해줌
* **가장 기본**적인 저장 방식
* `LLM이 허용하는 범위 이상을 넘어서게 되면 `Memory` 제어를 해줘야하는 불편함이 있음

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory();
memory.save_context(
    inputs={
        "user": "안녕하세요. 1+4는 뭔가요?"
    },
    outputs={
        "assistant": "1+4는 5입니다."
    }
)

print(memory)
```


* 결과
```
ConversationBufferMemory(chat_memory=InMemoryChatMessageHistory(messages=[
HumanMessage(content='안녕하세요. 1+4는 뭔가요?', additional_kwargs={}, response_metadata={}), 
AIMessage(content='1+4는 5입니다.', additional_kwargs={}, response_metadata={})]))
```

`ConversationBufferMemory` 생성 시 `return_messages`를 `True`로 주게 된다면  
Message 객체(`HumanMessage`, `AIMessage`)를 반환 받을 수 있다  

```python
memory.load_memory_variables({})["history"]
```

* 결과
```
[HumanMessage(content='안녕하세요. 1+4는 뭔가요?', additional_kwargs={}, response_metadata={}),
 AIMessage(content='1+4는 5입니다.', additional_kwargs={}, response_metadata={}),
 HumanMessage(content='안녕하세요. 5+2는 뭔가요?', additional_kwargs={}, response_metadata={}),
 AIMessage(content='5+2는 7입니다.', additional_kwargs={}, response_metadata={}),
 HumanMessage(content='안녕하세요. 12*3은 뭔가요?', additional_kwargs={}, response_metadata={}),
 AIMessage(content='12*3은 36입니다.', additional_kwargs={}, response_metadata={})]
```

