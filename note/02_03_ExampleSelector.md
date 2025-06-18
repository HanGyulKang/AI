## Example Selector
- **정의** : 질의와 유사도 계산을 해서 몇 개의 질문만 넣어줌(**토큰 절약**)
- **참고** : [링크](https://python.langchain.com/v0.1/docs/modules/model_io/prompts/example_selectors/)

#### Data Init
```python
few_shot_examples = [
    {
        "question": "파리와 런던 중 어느 도시가 더 인구가 많나요?",
        "answer": """
            이 질문에 추가 질문이 필요한가요: 예.
            추가 질문: 파리의 인구는 얼마나 되나요?
            중간 답변: 파리의 인구는 약 210만 명입니다.
            추가 질문: 런던의 인구는 얼마나 되나요?
            중간 답변: 런던의 인구는 약 890만 명입니다.
            최종 답변은: 런던
        """,
    },
    {
        "question": "태양과 달 중 어느 것이 지구에서 더 멀리 있나요?",
        "answer": """
            이 질문에 추가 질문이 필요한가요: 예.
            추가 질문: 태양까지의 거리는 얼마나 되나요?
            중간 답변: 태양까지의 거리는 약 1억 5천만 km입니다.
            추가 질문: 달까지의 거리는 얼마나 되나요?
            중간 답변: 달까지의 거리는 약 38만 km입니다.
            최종 답변은: 태양
        """,
    },
    {
        "question": "코끼리와 기린 중 어느 동물이 더 무겁나요?",
        "answer": """
            이 질문에 추가 질문이 필요한가요: 예.
            추가 질문: 아프리카 코끼리의 평균 체중은 얼마나 되나요?
            중간 답변: 아프리카 코끼리의 평균 체중은 약 6톤입니다.
            추가 질문: 기린의 평균 체중은 얼마나 되나요?
            중간 답변: 기린의 평균 체중은 약 1.2톤입니다.
            최종 답변은: 코끼리
        """,
    },
]
```

> [ **Embedding** 짤 지식 ]
>* embedding의 목적 : 문장은 숫자가 아니기 때문에 유사성을 판단할 수가 없음. 그래서 문장을 숫자로 변환해서 데이터베이스에 넣어두고 유사도를 판단함.
>>
>* 유사도 판단 방법 : 비슷한 의미의 문장들은 비슷한 숫자(벡터)로 변환됨. 예를 들어 "고양이"와 "강아지"는 "동물"이라는 의미로 비슷한 벡터를 가지게 되고, 두 벡터 사이의 거리를 계산해서 유사도를 측정함.
>
> 더 자세한 내용은 추후에...

### SemanticSimilarityExampleSelector
```python
from langchain_core.example_selectors import (
    MaxMarginalRelevanceExampleSelector,
    SemanticSimilarityExampleSelector,
)
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Vector DB 생성
chroma = Chroma("example_selector", OpenAIEmbeddings())

COUNT = 1

example_selector = SemanticSimilarityExampleSelector.from_examples(
    # 선택해야할 예시
    few_shot_examples,
    # Embedding Class
    OpenAIEmbeddings(),
    # Vector Store
    Chroma,
    # few shot examples에서 선택할 예제 개수
    k=COUNT,
)

question = "서울에서 부산까지 거리는 얼마나 되나요?"
selected_examples = example_selector.select_examples({"question": question})

# few shot templates 중 유사한 예시만 COUNT 값만큼 추출
for example in selected_examples:
    print(f'question:\n{example["question"]}')
    print(f'answer:\n{example["answer"]}')
```