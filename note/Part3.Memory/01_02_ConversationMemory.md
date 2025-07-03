# ConversationBufferMemory

---

* 메시지를 저장한 다음 변수에 메시지를 추출할 수 있게 해줌
* **가장 기본**적인 저장 방식
* `LLM`이 허용하는 범위 이상을 넘어서게 되면 오류가 발생하기 때문에 `Memory` 제어를 해줘야하는 불편함이 있음

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

# ConversationBufferWindowMemory

---

* Window : 한 번의 오고간 대화
* 사전에 최근의 얼마만큼의 `Window`만큼 저장할지 제약을 둘 수 있음
  * 쉽게 말해 그냥 최근 주고받은 대화 몇 개를 저장할 것인지 지정하는 것

```python
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(k=2, return_messages=True)
```
여기에서 `k`가 `Window`의 개수이다.  
해당 기능으로 오래된 대화를 적절하게 제거해주고 최근 대화 기준으로 대화를 이어갈 수 있는 장점이 있다.

# ConversationTokenBufferMemory

---

* 최근 대화 히스토리를 메모리에 보관하고, 대화의 개수가 아닌 **토큰의 길이**를 기준으로 대화 내용을 `Flush`할 시기를 결정한다.
* 비용은 대화 개수가 아닌 `Token`의 양으로 결정되기 때문에 비용 계산 측면에서 `TokenBufferMemory`가 더 유용하다.

```python
from langchain.memory import ConversationTokenBufferMemory

llm = {some llm}

memory = ConversationTokenBufferMemory(
    llm=llm, 
    max_token_limit=150, # 150 토큰만 저장
    return_messages=True
)
```


# ConversationEntityMemory

---

* 대화의 양(`Window`, `Token`)으로 제어하는 것이 아님
* 기존 메모리 저장 방식은 최근 대화 기준으로 특정 양을 저장하기 때문에 대화가 길어지면 결과가 다소 아쉬워질 수 있음
* `Entity` 즉 어떠한 특정 정보를 저장하는 것이 `ConversationEntityMemory`
  * 특정 정보에 대해 저장하기 때문에 효율성이 높음
* 단, `Entity`정보를 추출하고 축적하는데 모두 `LLM`을 사용한다.

`Entity`저장 내역을 꺼내려면?
```python
print(conversation.memory.entity_store.store)
```

[예제 코드](../code/ConversationEntityMemory.py)
* 결과 : `GPT`사용을 안 하고 `Ollama`에 있는 `llava:7b`를 사용해서 그런지 조금 이상하긴 함
```json
{
  "Han": "Han is a couple who are both developers and they got married two years ago. They are planning to go on a trip abroad.",
  "Ura": "Ura is a couple who are both developers and they got married two years ago. They are planning to go on a trip abroad.",
  "개발자": "Existing summary of 개발자:\n한결과 유라는 서로 부부하다. 그들은 2년전에 결혼했으며 해외 여행을 갈 계획을 세우고 있습니다.\nUpdated summary:\n한결과 유라는 서로 부부하다. 그들은 2년전에 결혼했으며 해외 여행을 갈 계획을 세우고 있습니다.",
  "유라": "Existing summary of 유라:\n유라는 서로 부부하다. 그들은 2년전에 결혼했으며 해외 여행을 갈 계획을 세우고 있습니다.",
  "2년전": "Existing summary of 2년전:\n2년전에 한결과와 유라가 결혼했다.",
  "결혼": "Existing summary of 결혼:\n한결과 유라는 서로 부부하다. 그들은 2년전에 결혼했으며 해외 여행을 갈 계획을 세우고 있습니다.\nUpdated summary:\n한결과 유라는 서로 부부하다. 그들은 2년전에 결혼했으며 해외 여행을 갈 계획을 세우고 있습니다.",
  "해외 여행": "The couple, Han-yeol and Yu-ra, are planning a trip abroad."
}
```

# ConversationKGMemory

---

* KG : **Knowledge Graph**(지식그래프)
* 즉, 지식 그래프를 활용한 `Memory`
* `LLM`이 서로 다른 개체간의 관계를 이해하게 하고, 복잡한 연결망과 History의 맥락을 기반으로 대응할 수 있게 함
  * 너와 나의 연결고리
* `Entity` 메모리와 비슷함

[예제 코드](../code/ConversationKGMemory.py)