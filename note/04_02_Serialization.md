# 직렬화(Serialization)

- **정의**
  - 모델을 저장 가능한 형식으로 변환하는 과정
    - 생성한 Chain을 저장할 목적
    - 직렬화 과정을 통해서 **JSON 형식으로 변경 후 저장**함
- **목적**
  - 모델 재사용(재훈련 불필요)
  - 모델 배포 및 공유
  - 계산 리소스 절약
  - 빠른 모델 로딩
  - 버전 관리
  - 다양한 환경에서 활용
- **주의**
  - 직렬화가 가능하지 않은 경우도 존재 함

## 직렬화

```python
from langchain_core.load import dumpd, dumps

chain = prompt | llm
chain.is_lc_serializable() # 생성한 체인이 직렬화 가능한지 : return true/false

# dumps : JSON 형식
dumps_chain = dumps(chain)
# dumpd : 딕셔너리 타입
dumpd_chain = dumpd(chain)
```

## 저장
### Pickle (**추천**)

```python
import pickle
with open("filename.pkl", "wb") as file: # 확장자는 자유롭게 해도 됨
    Pickle.dump(dumpd_chain, file)
```

### JSON

```python
import json

with open("filename.json", "w") as file:
    json.dump(dumps_chain, file)
```

## 불러오기

### Pickle
```python
import langchain_core.load import load
import pickle

with open("filename.pkl", "wb") as file:
    loaded_chain = pickle.load(file)

chain_from_file = load(loaded_chain)

# chain 실행
response = chain_from_file.invoke({"question":"some question"})
print(response)
```

### JSON
```python
import langchain_core.load import load
import json

with open("fruit_chain.json", "r") as file:
    loaded_from_json_chain = json.load(file)
    loads_chain = load(loaded_from_json_chain)

response = loads_chain.invoke({"question":"some question"})
print(response)
```