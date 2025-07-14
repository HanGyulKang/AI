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
- **정의**
  - cosine similarity(유사도 계산)
- **한계**
  - 유사도만으로 선택하면 너무 비슷한 예제들만 선택될 수 있음

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
    few_shot_examples,  # 선택해야할 예시
    OpenAIEmbeddings(), # Embedding Class
    Chroma,             # Vector Store
    k=COUNT,            # few shot examples에서 선택할 예제 개수
)

question = "서울에서 부산까지 거리는 얼마나 되나요?"
selected_examples = example_selector.select_examples({"question": question})

# few shot templates 중 유사한 예시만 COUNT 값만큼 추출
for example in selected_examples:
    print(f'question:\n{example["question"]}')
    print(f'answer:\n{example["answer"]}')
```

### MaxMarginalRelevanceExampleSelector
- **정의**
  - 줄여서 **MMR**로 보통 표현 함
  - 관련성은 유지하면서도 **다양한 관점의 예제들을 선택**함
  - 관련성(Relavance)
    - 검색 쿼리나 주제와 문서의 관련성을 평가 함. 문서와 주어진 쿼리의 일치성을 점수로 표현 함
  - 다양성(Diversity)
    - 이미 선택된 문서와의 유사성을 평가 함. 단, 선택 과정에서 문서간의 다양성을 보장 함.
  - 알고리즘 과정
    - 가장 관련성 높은 항목 선택
    - 관련성이 높으면서도 차별화된 항목을 찾아 선택
    - Lambda(λ) 계수가 작으면 다양성, 클수록 관련성을 더 많이 참고를 함.
      - 0 ~ 1 사이인 0.5를 선택하면 관련성과 다양성을 동등하게 고려 함 (일반적으로 권장 됨)
      - 1 : SSE와 동일
      - 0 : 다양성만 고려

##### MMR 공식
```
MMR = λ × Relevance(D) - (1-λ) × max(Similarity(D, D_i))
```


##### 사용 예시
```python
example_selector = MaxMarginalRelevanceExampleSelector.from_examples(
    few_shot_examples,
    OpenAIEmbeddings(),
    Chroma,
    k=2,             # 2개 예제 선택
    fetch_k=10,      # 후보로 10개를 가져와서
    lambda_mult=0.5  # λ=0.5로 다양성과 관련성 균형
)
```

##### 언제 사용할까?
- **SemanticSimilarityExampleSelector 사용 시**: k=3으로 설정했는데 너무 비슷한 예제들만 선택될 때
- **다양한 관점이 필요할 때**: 같은 주제라도 다른 접근 방식의 예제들이 필요할 때
- **토큰 효율성을 높이고 싶을 때**: 비슷한 예제 대신 다양한 예제로 더 많은 정보를 제공하고 싶을 때

## ExampleSelector의 문제점
