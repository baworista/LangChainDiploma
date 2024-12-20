from langchain_openai import ChatOpenAI

from auth_utils import auth_func

auth_func()

llm = ChatOpenAI(model_name='gpt-4o-mini', temperature=0.4, max_tokens=500)

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

dsafadsf = 'gay'
agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            'system',
            f"You are an onlyfans porn actor from America in 2024. Provide a discussion with your opponent with provided topic",
        ), MessagesPlaceholder(variable_name='messages'),
    ]
)

reviewer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            'system',
            "You are a priest from catolic church in Poland in 2024. Provide a discussion with your opponent with provided topic",
        ), MessagesPlaceholder(variable_name='messages'),
    ]
)

agent_chain = agent_prompt | llm
reviewer_chain = reviewer_prompt | llm
