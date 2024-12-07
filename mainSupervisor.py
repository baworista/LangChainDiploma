from langchain_core.messages import SystemMessage
from auth_utils import auth_func
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

auth_func()
model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0, max_tokens=300)

user_message = HumanMessage(content=f"Tell me about Miami")

messages = [
    SystemMessage(content="You are helpful AI assistant"),
    user_message,
]

response = model.invoke(messages)

print(response)