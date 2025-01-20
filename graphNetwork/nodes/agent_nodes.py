import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from graphNetwork.states import OveralState
from graphNetwork.schemas import Output



load_dotenv()



# Initialize LLM
llm = ChatOpenAI(model=os.getenv("MODEL_SUPERVISOR"))
model = llm.with_structured_output(Output)

from graphNetwork.prompts.generators import create_user_prompt, generate_agent_prompt


# Generic agent handler
def agent_handler(state: OveralState, agent_prompt: str):
    user_prompt = create_user_prompt(state)

    messages = [
        {"role": "system", "content": agent_prompt},
        {"role": "user", "content": user_prompt}
    ]
    ai_msg = model.invoke(messages)

    print("""
RESPONSE\n" 
{ai_msg.analysis}
==========================\n
NEXT AGENT: {ai_msg.next_agent}
TASK: {ai_msg.task}
QUESTIONS: {ai_msg.questions}
==========================\n
    """.format(ai_msg=ai_msg))

    if ai_msg.next_agent != "__end__":
        return Command(
            goto=ai_msg.next_agent,
            update={
                "analysis": [ai_msg.analysis],
                "task": ai_msg.task,
                "questions": ai_msg.questions,
                "processed_agents": [ai_msg.name, ai_msg.next_agent],
            }
        )

    return {"analysis": [ai_msg.analysis]}

# Define agents
def Consulting_Agent(state: OveralState):
    return agent_handler(state, generate_agent_prompt("Consulting_Agent"))

def HR_Agent(state: OveralState):
    return agent_handler(state, generate_agent_prompt("HR_Agent"))

def BP_Agent(state: OveralState):
    return agent_handler(state, generate_agent_prompt("BP_Agent"))

def KM_Agent(state: OveralState):
    return agent_handler(state, generate_agent_prompt("KM_Agent"))

def IT_Agent(state: OveralState):
    return agent_handler(state, generate_agent_prompt("IT_Agent"))