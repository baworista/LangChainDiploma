import os

from dotenv import load_dotenv
from langchain.agents import create_react_agent
from langchain_core.agents import AgentFinish
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain import hub
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor

from graphNetwork.schemas import Response
from langchain_community.tools import TavilySearchResults

from graphNetwork.states import OverallState, AgentState

load_dotenv()

prompt: PromptTemplate = hub.pull("hwchase17/react")

llm = ChatOpenAI(model_name=os.getenv("MODEL"))
structured_llm = llm.with_structured_output(Response)

tools = [TavilySearchResults(max_results=1)]
react_agent_runnable = create_react_agent(tools=tools, llm=llm, prompt=prompt)

def run_agent_reasoning_engine(state: AgentState):
    agent_outcome = react_agent_runnable.invoke(state)
    return {"agent_outcome": agent_outcome}

tool_executor = ToolExecutor(tools)

def execute_tools(state: AgentState):
    agent_action = state["agent_outcome"]
    output = tool_executor.invoke(agent_action)
    return {"intermediate_steps": [(agent_action, str(output))]}


def reActAgent(state: OverallState):
    AGENT_REASON = "agent_reason"
    ACT = "act"

    def should_continue(state: AgentState) -> str:
        if isinstance(state["agent_outcome"], AgentFinish):
            return END
        return ACT

    flow = StateGraph(AgentState)

    flow.add_node(AGENT_REASON, run_agent_reasoning_engine)
    flow.set_entry_point(AGENT_REASON)
    flow.add_node(ACT, execute_tools)

    flow.add_conditional_edges(AGENT_REASON, should_continue)

    flow.add_edge(ACT, AGENT_REASON)
    return flow

