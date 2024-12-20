import json
from typing import List, Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langchain.tools import tool

from graphSupervisor.state import OverallState, AnalystState

from auth_utils import auth_func

auth_func()
# Инициализация LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Инструкции для создания аналитиков
analyst_instructions = """
You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:

1. Human Resources Analyst: Focus on team dynamics, collaboration, and training.
2. Business Process Analyst: Focus on process optimization and automation.
3. Knowledge Management Analyst: Focus on knowledge sharing and tools.
4. IT Systems Analyst: Focus on IT strategies and systems.
"""


@tool
def create_analysts_tool(topic: str) -> List[Dict]:
    """
    Генерирует список аналитиков на основе темы.
    """
    system_message = SystemMessage(content=analyst_instructions)
    human_message = HumanMessage(content=f"Here is the topic: {topic}. Generate analysts.")

    # Запрос к LLM для создания аналитиков
    response = llm.invoke([system_message, human_message])
    return json.loads(response.content)["analysts"]


@tool
def write_report_tool(state: OverallState) -> Dict:
    """
    Создаёт финальный отчёт, агрегируя результаты аналитиков.
    """
    aggregated_diagnosis = []
    aggregated_recommendations = []

    # Сбор данных аналитиков
    for analyst in state["analysts"]:
        aggregated_diagnosis.extend(analyst.get("diagnosis", []))
        aggregated_recommendations.extend(analyst.get("recommendations", []))

    # Формирование отчёта
    report = f"""
    **Consulting Report for Topic: {state['topic']}**

    **Diagnoses:**
    {json.dumps(aggregated_diagnosis, indent=2)}

    **Recommendations:**
    {json.dumps(aggregated_recommendations, indent=2)}
    """
    return {"final_report": report.strip()}


def create_analyst_subgraph(analyst: AnalystState) -> StateGraph:
    """
    Создаёт подграф для аналитика.
    """
    graph = StateGraph(state_schema=AnalystState)
    graph.add_node("analysis", lambda state: {
        "diagnosis": [f"Diagnosis from {analyst['name']}"],
        "recommendations": [f"Recommendation from {analyst['name']}"]
    })
    graph.add_edge(START, "analysis")
    graph.add_edge("analysis", END)
    return graph


def supervisor_node(topic: str):
    """
    Основной узел, управляющий аналитиками и графом.
    """
    # Создаём основной граф
    main_graph = StateGraph(state_schema=OverallState)
    main_graph.add_node(START)

    # Генерация аналитиков
    analysts = create_analysts_tool(topic)
    analyst_subgraphs = {}

    # Создание подграфов для каждого аналитика
    for analyst_data in analysts:
        analyst_state = AnalystState(
            analyst_name=analyst_data["name"],
            topic=topic,
            goals=f"Role: {analyst_data['role']}",
            diagnosis=[],
            recommendations=[]
        )
        analyst_subgraphs[analyst_data["name"]] = create_analyst_subgraph(analyst_state)
        subgraph_name = f"{analyst_data['name']}_subgraph"
        main_graph.add_node(subgraph_name, analyst_subgraphs[analyst_data["name"]])
        main_graph.add_edge(START, subgraph_name)

    # Финальный узел для отчёта
    main_graph.add_node("write_report", lambda state: write_report_tool(state))
    main_graph.add_edge(START, "write_report")
    main_graph.add_edge("write_report", END)

    # Компиляция и выполнение
    app = main_graph.compile(input={"topic": topic}, output=lambda state: state["final_report"])
    return app.invoke({})


# Пример использования
if __name__ == "__main__":
    topic = "Digital Transformation in Organizations"
    report = supervisor_node(topic)
    print(report)
