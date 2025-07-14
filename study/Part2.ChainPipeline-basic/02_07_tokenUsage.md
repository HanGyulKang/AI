# 토큰 사용량 확인
## GPT 밖에 안 됨

---

```python
from langchain.callbacks import get_openai_callback

with get_openai_callback() as cb:
    result = llm.invoke("1+2는 뭐야?")
    print(f"총 사용된 토큰수: \t\t{cb.total_tokens}")
    print(f"프롬프트에 사용된 토큰수: \t{cb.prompt_tokens}")
    print(f"답변에 사용된 토큰수: \t{cb.completion_tokens}")
    print(f"호출에 청구된 금액(USD): \t${cb.total_cost}")
```