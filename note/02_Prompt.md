```python
from langchin_core.prompts import PromptTemplate

template = "{num1} 더하기 {num2}의 결과는?"
```

## from_template

```python
prompt = PromptTemplate.from_template(template)

prompt.format(num1=5, num2=2)
print(prompt)
```

## PromptTemplate 객체 생성 시 즉시 Prompt 생성

```python
prompt = PromptTemplate(
    template=template,
    input_variables=["num1", "num2"]
)

prompt.format(num1=5, num2=2)
print(prompt)
```

#### 미리 변수 값 초기화해서 준비하기

```python
prompt = PromptTemplate(
    template=template,
    input_variables=["num1"],
    partial_variables={ # 이런 방식으로 미리 값을 준비할 수 있지만, 동일한 키로 새로운 값이 들어오면 덮어씌워진다.
        "num2": 12
    },
)

prompt.format(num1=3)
print(prompt)
```

- **부가설명**
  - 보통의 경우에 그냥 값을 넣어둔다기보다는 함수를 넣어주는 경우가 많음.
  - 이를테면 오늘날짜를 구하는 함수를 만들어서 함수 자체를 partial_variables에 셋팅해줄 수 있음.

## 파일(.yaml)에서 로드

#### 파일 형식
```yaml
# dir/test.yaml
_type: "prompt"
template: | # 파이프(|)를 사용하게 되면 개행 문자열도 사용할 수 있음
  두칸 띄고 작성하면 됨
  이런식으로
  {var1} + {var2} = ?
input_variables: ["var1", "var2", ...]
```

```python
from langchain_core.prompts import load_prompt

prompt = load_prompt("dir/test.yaml", encoding="utf-8")
prompt.format(var1=2, var2=5)
```

### ChatPromptTemplate

- **role**
  - system : 시스템 설정 메시지. 전역설정
  - human : 사용자 입력, 질의 메시지
  - ai : AI의 답변 메시지

```python
from langchain_core.prompts import ChatPromptTemplate

# --- 1
prompt = ChatPromptTemplate.from_template(template)
prompt.format(num1=3, num2=7)

# --- 2
prompt = ChatPromptTemplate.from_message(
    [
        # role, message
        ("system", "너는 {age}살 수학 선생님이야."),
        ("human", "안녕"),
        ("ai", "안녕하세요. 저는 수학선생님이예요."),
        ("human", "{user_input}"),
    ],
)

messages = ChatPromptTemplate.format_messages(
    age=38, user_input="선생님은 몇살이세요?"
)

# --- 1. 이렇게 뽑거나
# llm.invoke(messages)

# --- 2. 이렇게 연결해서 뽑거나
# chain = prompt | llm | StrOutputParser()
# chain.invoke({"age" : 38, "user_input" : "선생님은 몇살이세요?"}).content
```