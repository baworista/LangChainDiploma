import os
from typing import Annotated, Literal
from dotenv import load_dotenv
from langchain_core.agents import AgentFinish
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import create_react_agent, InjectedState
from langchain_openai import ChatOpenAI
from langchain import hub
from langgraph.constants import END
from graphNetwork.states import CustomAgentState
from langgraph.types import Command
from langchain_community.tools import TavilySearchResults


llm = ChatOpenAI(model_name=os.getenv("MODEL"))


@tool
def ask_tool(question_to: str, question_from: str, question: str):
    """
    Asks another agent a question.

    This function enables an agent to ask a question to another agent. It updates the state
    with the question and navigates to the target agent node in the parent graph.

    :param question_to: Code name of the agent to ask the question to.
    :param question_from: Code name of the current agent asking the question.
    :param question: The content of the question to be asked.
    :return: Command object to navigate to the target agent node with updated state.
    """

    print(question_from + " asks " + question_to + "!")
    return Command(
        # navigate to another agent node in the PARENT graph
        goto=question_to,
        graph=Command.PARENT,
        # This is the state update that the agent `agent_name` will see when it is invoked.
        # We're passing agent's FULL internal message history AND adding a tool message to make sure
        # the resulting chat history is valid.
        update={"questions_from_agents": {question_from: question}},
    )


@tool
def answer_tool(answer_from: str, answer_to: str, answer: str):
    """
    Answers another agent's question.

    This function enables an agent to answer a question from another agent. It updates the state
    with the answer and navigates to the target agent node in the parent graph.

    :param answer_to: Code name of the agent who asked the question and to whom the answer should be sent.
    :param answer_from: Code name of the current agent providing the answer.
    :param answer: The content of the answer to be provided.
    :return: Command object to navigate to the target agent node with updated state.
    """

    print(answer_from + " answers to " + answer_to + "!")
    return Command(
        # navigate to another agent node in the PARENT graph
        goto=answer_to,
        graph=Command.PARENT,
        # This is the state update that the agent `agent_name` will see when it is invoked.
        # We're passing agent's FULL internal message history AND adding a tool message to make sure
        # the resulting chat history is valid.
        update={"answers_from_agents": {answer_from: answer}},
    )


prompt = """
You are an agent {name} specializing in {role}. Your code name is {code_name}. Use it in question-asking tools.

Your task is to assist in analyzing and resolving key issues related to the topic "{topic}".  
You have the following responsibilities:
{description}

Your team consists of (one of them is you): 
    a. **HR_Agent**: Focused on HR issues like team dynamics, performance, and training.
    b. **BP_Agent**: Specializing in process optimization and automation.
    c. **KM_Agent**: Concentrating on knowledge sharing and tools.
    d. **IT_Agent**: Addressing IT strategies and tools.

### Working Process:
1. **Initial Analysis**:  
   - Start by creating an **Initial Analysis** based on the topic and your specific role. 
   - The Initial Analysis will serve as the foundation for asking questions to other agents. 

2. **Questioning Other Agents**:  
   - After completing your Initial Analysis, formulate **one question** for each of the other three agents (**HR_Agent**, **BP_Agent**, **KM_Agent**, or **IT_Agent**).  
   - These questions should clarify or enhance your understanding of their specific areas of expertise related to the topic.
   - Use the `ask_tool` to send these questions. Ensure that your code name `{code_name}` is included in the question metadata.

3. **Answering Questions**:  
   - You will receive **three questions** from the other agents.  
   - Answer each question using your **Initial Analysis**, your current context, and your memory of the discussion so far.  
   - Providing answers to questions has the **highest priority**.

4. **Final Summary**:  
   - After answering the three incoming questions and asking three outgoing questions, use your full context, including your Initial Analysis, the answers you've given, and the responses you’ve received, to create a **Final Summary**.  
   - The Final Summary should encapsulate your insights, recommendations, and conclusions related to the topic and your responsibilities.  

### Important Notes:
- You can only ask **one question per agent**.
- Ensure your responses are detailed, accurate, and specific to your area of expertise.
- Do not forget to include human-readable explanations and reasoning in all your interactions (Initial Analysis, questions, answers, and Final Summary).
"""




def call_agent(state: CustomAgentState):
    agent_prompt=prompt.format(
        code_name=state['code_name'],
        name=state['name'],
        role=state['role'],
        topic=state['agent_topic'],
        questions=state['agent_questionnaire'],
        description=state['description'],
    )

    code_name = state["code_name"]
    tools = [TavilySearchResults(max_results=1), ask_tool, answer_tool] # Create tools dynamically, excluding the current agent

    agent = create_react_agent(llm, tools, state_modifier=agent_prompt, state_schema=CustomAgentState)

    print("Agent " + code_name + " has been invoked!")

    # if "questions_from_agent" not in state or not state["questions_from_agents"]:
    #     print("There is no questions")
    # else:
    #     for question in state["questions_from_agents"]:


    # # Генерация Mermaid-графа с улучшенным расположением и цветами
    # graph_image = agent.get_graph(
    #     xray=2,
    # ).draw_mermaid_png()
    #
    # # Сохранение графа
    # with open("react_graph_diagram.png", "wb") as file:
    #     file.write(graph_image)
    # print("Network graph diagram saved as 'react_graph_diagram.png'")
    response = agent.invoke(state)
    return {"reviews": [response]}




























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
