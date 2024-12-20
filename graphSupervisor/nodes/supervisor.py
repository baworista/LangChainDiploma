from typing import List

from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from auth_utils import auth_func
from graphSupervisor.nodes.analyst import analyst_node
from graphSupervisor.state import OverallState, Perspectives, AnalystState

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


@tool
def write_report(state: OverallState):
    """
    Объединяет результаты всех аналитиков и формирует финальный отчет.

    Args:
        state (OverallState): Состояние, содержащее результаты всех аналитиков.

    Returns:
        dict: Обновленное состояние с финальным отчетом.
    """
    print("... Write Report ...")

    aggregated_diagnosis = []
    aggregated_recommendations = []

    # Сбор данных из консультирования
    for analyst in state["analysts"]:
        diagnosis = analyst.get("diagnosis", [])
        recommendations = analyst.get("recommendations", [])
        aggregated_diagnosis.extend(diagnosis)
        aggregated_recommendations.extend(recommendations)

    # Инструкции для генерации отчёта
    writing_instructions = """
    You are an expert tasked with summarizing the findings of a consulting process.
    Use the following structure to create the report:

    1. Introduction: Provide a brief summary of the consulting process.
    2. Diagnoses: Summarize the key diagnoses in a concise and clear manner.
    3. Recommendations: Provide actionable recommendations for the client.
    4. Conclusion: Conclude the report with a forward-looking statement.

    Diagnoses:
    {diagnosis}

    Recommendations:
    {recommendations}
    """

    # Формирование сообщения для LLM
    system_message = writing_instructions.format(
        diagnosis="\n".join(aggregated_diagnosis),
        recommendations="\n".join(aggregated_recommendations),
    )

    # Генерация отчёта с помощью LLM
    report_response = llm.invoke([SystemMessage(content=system_message)])
    final_report = report_response.content.strip()

    # Формирование итогового состояния
    state["aggregated_diagnosis"] = aggregated_diagnosis
    state["aggregated_recommendations"] = aggregated_recommendations
    state["final_report"] = final_report

    print("Final report generated.")
    return state


def supervisor_decision(state: OverallState):
    """
    Invokes the supervisor decision function.
    """
    current_step = state.get("current_step", 0)
    max_steps = 4  # Number of analysts
    state["current_step"] = current_step + 1

    if current_step < max_steps:
        return ["HRAnalyst", "BPAnalyst", "KMAnalyst", "ITAnalyst"][current_step]
    return END


@tool
def initiate_consulting_threads(topic: str, analysts: List[dict]) -> dict:
    """
    Initiate parallel agent workflow using isolated substates for each analyst.

    Args:
        topic (str): The overall topic of analysis.
        analysts (List[dict]): List of analyst definitions containing name, role, and description.
        questionnaire (str): The questionnaire results or user input.

    Returns:
        Dict[str, AnalystState]: Dictionary of individual analyst states indexed by their names.
    """
    print("... Initiate analysis ...")
    print(f"Analysts: {analysts}")
    print(f"Topic: {topic}")

    # Create individual states for each analyst
    analyst_states = {}
    for analyst in analysts:
        analyst_state = AnalystState(
            analyst_name=analyst["name"],
            topic=topic,
            goals=f"Role: {analyst['role']}\nDescription: {analyst['description']}",
            diagnosis=[],
            recommendations=[],
        )
        analyst_states[analyst["name"]] = analyst_state

    return analyst_states  # should be dict for state to update


def supervisor_node(state: OverallState):
    """
    Invokes the supervisor node and dynamically adds analyst nodes to the graph.
    """

    # Check if there are agents
    if "analysts" not in state or not state["analysts"]:
        # Generate analysts
        generated_analysts = create_analysts_tool.invoke(state["topic"])
        state.update(generated_analysts)
        state["analyst_progress"] = {analyst["name"]: False for analyst in state["analysts"]}

        # Generate individual analyst states
        input_payload = {"topic": state["topic"], "analysts": state["analysts"]}
        analyst_states = initiate_consulting_threads.invoke(input_payload)  # Ensure both fields are passed

        # Add dynamic nodes to the graph
        for analyst_state in analyst_states.items():
            create_analyst_subgraph(analyst_state)
            print(analyst_state)

    # Invoke tools to process the state
    tools = [initiate_consulting_threads, write_report]
    tool_mapping = {tool.name.lower(): tool for tool in tools}
    print(tool_mapping)

    llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

    # Call tools
    response = llm_with_tools.invoke(state)
    print("Response from llm with tools:", response.tool_calls)

    for tool_call in response.tool_calls:
        tool_name = tool_call["name"].lower()
        tool_args = tool_call["args"]

        # Check if the tool exists in the mapping
        if tool_name not in tool_mapping:
            raise ValueError(f"Tool '{tool_name}' not found in the defined tools.")

        selected_tool = tool_mapping[tool_name]
        tool_response = selected_tool.run(tool_args)  # Use `run` to correctly pass arguments
        print(f"Output from tool '{tool_name}':", tool_response)

        # Update only specific fields in the state
        state.update(tool_response)

    return state


def create_analyst_subgraph(analyst_state: AnalystState):
    """
    Создаёт подграф для отдельного аналитика.
    """
    subgraph = StateGraph(state_schema=AnalystState)

    # # Добавление узлов подграфа
    # subgraph.add_node("analysis", lambda state: {
    #     "diagnosis": [f"Diagnosis by {analyst_state['name']}"],
    #     "recommendations": [f"Recommendation by {analyst_state['name']}"]
    # })

    subgraph.add_node("analysis", analyst_node)

    # Установка последовательности выполнения
    subgraph.add_edge(START, "analysis")
    subgraph.add_edge("analysis", END)

    subApp = subgraph.compile()

    # Save as PNG
    graph_image = subApp.get_graph().draw_mermaid_png()
    with open("updated_graph_diagram.png", "wb") as file:
        file.write(graph_image)
    print("Saved as PNG 'updated_graph_diagram.png'")

    return subApp

# # Example usage
# if __name__ == "__main__":
#     # Mock OverallState for demonstration
#     state = OverallState(topic="Digital Transformation in Organizations")
#
#     print("initial_state: ", json.dumps(state, indent=4, ensure_ascii=False))
#
#     # Invoke the model with the tools and initial state
#     supervisor_node(state)
#
#     # Print the updated state
#     print("update_state:", json.dumps(state, indent=4, ensure_ascii=False))
