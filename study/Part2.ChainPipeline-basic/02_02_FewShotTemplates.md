```python
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
```

## Prompt Engineering 기법

- **Zero Shot**
  - 예시가 없음
- **One Shot** 
  - 하나의 답변 예시
- **Few Shot** 
  - 두 개 이상의 답변 예시

답변 예시를 AI에게 제공함으로써 답변의 질을 향상시킬 수 있음  
추론 자체를 도와주는 역할을 해줄 수 있고, Hallucination을 줄일 수 있음


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

example_prompt = PromptTemplate.from_template(
    "Question:\n{question}\nAnswer:\n{answer}"
)
```

#### Run
##### OneShotTemplate
```Python
example_prompt.format(**few_shot_examples[0]) # few shot examples에서 한 개만 추출
```
##### FewShotTemplate
```Python
prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Question:\n{question}\nAnswer:",
    input_variables=["question"],
)

# 만들어진 prompt 확인
question = "마이클 조던과 레브론 제임스 중 누가 더 많은 NBA 챔피언십을 우승했나요?"
final_prompt = prompt.format(question=question)
print(final_prompt)

# chain 생성 (pronpt + LLM + OutputParser)
chain = prompt | llm | StrOutputParser()

# 질의
answer = chain.stream(
    {"question": "마이클 조던과 레브론 제임스 중 누가 더 많은 NBA 챔피언십을 우승했나요?"}
)
```