import json
from langchain_core.messages import HumanMessage, SystemMessage
from auth_utils import auth_func
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from graphSupervisor.state import OverallState, Perspectives
from langchain.tools import tool

# Authenticate and initialize LLM
auth_func()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # should be gpt-4o

# Analyst creation instructions
analyst_instructions = """
You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:

First, review the provided research topic.

Next, create four AI analysts:
1. Human Resources Analyst, focusing on team dynamics and performance, team collaboration, and human trainings and development in the context of the topic.
2. Business Process Analyst, focusing on business process optimization, business process automation, and business process management in the context of the topic.
3. Knowledge Management Analyst, focusing on knowledge management processes, knowledge sharing, and knowledge tools in the context of the topic.
4. IT Systems Analyst, specializing in IT systems, IT tools, and IT strategies in the context of the topic.
"""


@tool
def create_analysts_tool(topic: str) -> dict:
    """
    Tool to create AI analysts based on a provided topic.
    Accepts the topic as a string and returns the generated analysts in a JSON-serializable format.
    """
    structured_llm = llm.with_structured_output(Perspectives)

    # Формируем запрос для LLM
    system_message = SystemMessage(content=analyst_instructions)
    human_message = HumanMessage(content=f"Generate the set of analysts. Here is the topic: {topic}.")

    # Генерация аналитиков
    perspectives: Perspectives = structured_llm.invoke([system_message, human_message])

    # Преобразуем в сериализуемый формат
    serialized_analysts = [
        {
            "name": analyst.name,
            "role": analyst.role,
            "description": analyst.description,
        }
        for analyst in perspectives.analysts
    ]

    return {"analysts": serialized_analysts}




def supervisor_decision(state: OverallState):
    """
    Determines which analyst the supervisor should talk to next. (Currently just for be)
    """
    current_step = state.get("current_step", 0)
    max_steps = 4  # Number of analysts
    state["current_step"] = current_step + 1

    if current_step < max_steps:
        return ["HRAnalyst", "BPAnalyst", "KMAnalyst", "ITAnalyst"][current_step]
    return END


def supervisor_node(state: OverallState):
    """
    Invokes the model with the provided tools and updates the state.
    """
    tools = [create_analysts_tool]
    tool_mapping = {tool.name.lower(): tool for tool in tools}
    print(tool_mapping)

    llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

    # Вызов инструмента для генерации аналитиков
    response = llm_with_tools.invoke(state["topic"])
    print("Response from llm with tools:", response.tool_calls)

    for tool_call in response.tool_calls:
        tool_name = tool_call["name"].lower()
        tool_args = tool_call["args"]

        # Check if the tool exists in the mapping
        if tool_name not in tool_mapping:
            raise ValueError(f"Tool '{tool_name}' not found in the defined tools.")

        selected_tool = tool_mapping[tool_name]
        tool_response = selected_tool.invoke(tool_args)  # Correctly use the invoke method
        print(f"Output from tool '{tool_name}':", tool_response)

        # Update only specific fields in the state
        state.update(tool_response)

    return state


# Example usage
if __name__ == "__main__":
    # Mock OverallState for demonstration
    state = OverallState(topic="Digital Transformation in Organizations")

    print("initial_state: ", json.dumps(state, indent=4, ensure_ascii=False))

    # Invoke the model with the tools and initial state
    supervisor_node(state)

    # Print the updated state
    print("update_state:", json.dumps(state, indent=4, ensure_ascii=False))




