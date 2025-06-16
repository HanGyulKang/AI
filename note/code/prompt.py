from langchain_core.prompts import PromptTemplate

template = "{num1} 더하기 {num2}의 결과는?"
prompt = PromptTemplate.from_template(template)

prompt.format(num1=5, num2=2)
print(prompt)

prompt.invoke({"num1": 5, "num2": 2})

# ------------------------------------------------------------

prompt = PromptTemplate(
    template=template,
    input_variables=["num1", "num2"]
)

prompt.format(num1=5, num2=2)
print(prompt)

prompt = PromptTemplate(
    template=template,
    input_variables=["num1"],
    partial_variables={
        "num2": 12
    }
)

prompt.format(num1=3)
print(prompt)

# ------------------------------------------------------------