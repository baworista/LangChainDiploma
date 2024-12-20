from langchain_core.prompts import ChatPromptTemplate

agent_prompt = ChatPromptTemplate.from_messages(
    [
        "system",
        "You work in a team on provided {topic}. Your goal is to review this topic and gice some recommendations"

    ]
)
