from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from llm_provider import llm

summary_prompt = PromptTemplate(
    input_variables=["user", "messages"],
    template="""
    以下是{user}最近的對話紀錄，請你幫我用繁體中文總結這段對話的主要內容：
    
    {messages}
    
    請只輸出重點摘要，不需要多餘敘述。
    """
)

def generate_summary(user: str, messages: list[str]) -> str:
    chain = LLMChain(llm=llm, prompt=summary_prompt)
    formatted_messages = "\n".join(messages[-5:])
    return chain.run(user=user, messages=formatted_messages)