import os
from typing import Annotated, Literal

from dotenv import load_dotenv
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import create_react_agent, InjectedState
from langchain_core.agents import AgentFinish
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain import hub
from langgraph.constants import END
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.types import Command
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langchain_community.tools import TavilySearchResults


llm = ChatOpenAI(model_name=os.getenv("MODEL"))


def make_handoff_tool(*, agent_name: str):
    """Create a tool that can return handoff via a Command"""
    tool_name = f"transfer_to_{agent_name}"

    @tool(tool_name)
    def handoff_to_agent(state: Annotated[dict, InjectedState], tool_call_id: Annotated[str, InjectedToolCallId], ):
        """Ask another agent for help."""
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": tool_name,
            "tool_call_id": tool_call_id,
        }

        print("handoff_to_agent " + agent_name + " has been invoked!")
        return Command(
            # navigate to another agent node in the PARENT graph
            goto=agent_name,
            graph=Command.PARENT,
            # This is the state update that the agent `agent_name` will see when it is invoked.
            # We're passing agent's FULL internal message history AND adding a tool message to make sure
            # the resulting chat history is valid.
            update={"messages": state["messages"] + [tool_message]},
        )

    return handoff_to_agent

@tool
def summary():
    """Summarizes provided text"""
    print("Report writer!")


def create_tools(code_name: str):
    handoff_tools = {
        "HR_Agent": make_handoff_tool(agent_name="HR_Agent"),
        "BP_Agent": make_handoff_tool(agent_name="BP_Agent"),
        "IT_Agent": make_handoff_tool(agent_name="IT_Agent"),
        "KM_Agent": make_handoff_tool(agent_name="KM_Agent"),
    }
    # Exclude the current agent from the tools
    return [TavilySearchResults(max_results=1)] + [summary] + [
        tool for name, tool in handoff_tools.items() if name != code_name
    ]

prompt = """
You are an agent {name} specializing in {role}. Your task is to assist in analyzing and resolving key issues related to the topic "{topic}". 
You have the following responsibilities:
{description}

Your team consists of: HR_Agent, BP_Agent, IT_Agent and KM_Agent

Perform an initial analysis based on the questions provided: {questions}.

If you need HR - recommendations, ask 'HR_Agent' for help.
If you need business processes recommendations, ask 'BP_Agent' for help.
If you need knowledge management recommendations, ask 'KM_Agent' for help.
If you need IT - recommendations, ask 'IT_Agent' for help.

You MUST include human-readable response before transferring to another agent.

When you have completed all questions. Summarize everything and provide a final analysis of the topic.

"""



def call_agent(state: AgentState) -> Command[Literal["HR_Agent", "BP_Agent", "IT_Agent", "KM_Agent", END]]:
    agent_prompt=prompt.format(
        name=state['name'],
        role=state['role'],
        topic=state['agent_topic'],
        questions=state['agent_questionnaire'],
        description=state['description'],
    )

    code_name = state["code_name"]
    tools = create_tools(code_name)  # Create tools dynamically, excluding the current agent

    agent = create_react_agent(llm, tools, state_modifier=agent_prompt)

    print("Agent " + code_name + " has been invoked!")

    # # Генерация Mermaid-графа с улучшенным расположением и цветами
    # graph_image = agent.get_graph(
    #     xray=2,
    # ).draw_mermaid_png()
    #
    # # Сохранение графа
    # with open("react_graph_diagram.png", "wb") as file:
    #     file.write(graph_image)
    # print("Network graph diagram saved as 'react_graph_diagram.png'")

    return agent.invoke(state)





















# "HR_Agent": reActAgent,
# "BP_Agent": reActAgent,
# "IT_Agent": reActAgent,
# "KM_Agent": reActAgent,


# from graphNetwork.schemas import Response
# from langchain_community.tools import TavilySearchResults
#
# from graphNetwork.states import OverallState, AgentState
#
# load_dotenv()
#
# prompt: PromptTemplate = hub.pull("hwchase17/react")
# # Основной промпт
#
# base_prompt = """
# You are an agent {name} specializing in {role}. Your task is to assist in analyzing and resolving key issues related to the topic "{topic}".
# You have the following responsibilities:
# {description}
# """
# # Дополнительные кусочки промпта
#
#
# additional_prompts = {
#     "initial_analysis": "\nPerform an initial analysis based on the questions provided: {questions}.",
#     "respond_to_question": "\nYou received a question from {sender}. Please answer it using your expertise.",
#     "final_analysis": "\nYou have completed all questions. Summarize your insights and provide a final analysis of the topic.",
# }
#
# structured_llm = llm.with_structured_output(Response)
#
# react_agent_runnable = create_react_agent(tools=tools, llm=llm, prompt=prompt)
#
#
# tool_executor = ToolNode(tools)
# # Функция для построения текущего промпта
#
#
# def build_agent_prompt(state: AgentState) -> str:
#     """
#     Создает текущий промпт для агента, основываясь на его состоянии и контексте.
#     """
#
#     prompt = base_prompt.format(
#         role=state["role"],
#         name=state["name"],
#         description=state["description"],
#         topic=state["topic"],
#     )
#
#     if state["questions_asked"] < 1:
#         prompt = prompt + additional_prompts["initial_analysis"].format()
#
#     if state["questions_asked"] >= 3:
#         prompt = prompt + additional_prompts["final_analysis"].format()
#
#     return prompt
#
#
# def run_agent_reasoning_engine(state: AgentState):
#
#
#
#
#
#
#     agent_outcome = react_agent_runnable.invoke(state)
#     return {"agent_outcome": agent_outcome}
#
#
# # def create_react_graph(state):
# #     AGENT_REASON = "agent_reason"
# #     ACT = "act"
# #
# #     def should_continue(state: AgentState)->str:
# #         if isinstance(state["agent_outcome"], AgentFinish):
# #             return END
# #         return ACT
# #
# #     flow = StateGraph(AgentState)
# #
# #     flow.add_node(AGENT_REASON, run_agent_reasoning_engine)
# #     flow.set_entry_point(AGENT_REASON)
# #     flow.add_node(ACT, execute_tools)
# #
# #     flow.add_conditional_edges(AGENT_REASON, should_continue)
# #
# #     flow.add_edge(ACT, AGENT_REASON)
# #
# #     return flow.compile()
#
# def execute_tools(state: AgentState):
#     agent_action = state["agent_outcome"]
#     output = tool_executor.invoke(agent_action)
#     return {"intermediate_steps": [(agent_action, str(output))]}
#
