from langchain_core.prompts import PromptTemplate

def template1() :
    template = "{num1} 더하기 {num2}의 결과는?"
    prompt = PromptTemplate.from_template(template)

    prompt.format(num1=5, num2=2)
    print(prompt)

def template2() :
    template = "{num1} 더하기 {num2}의 결과는?"
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

def main():
    print("=== Template 1 실행 ===")
    template1()
    print("\n=== Template 2 실행 ===")
    template2()

if __name__ == "__main__":
    main()

