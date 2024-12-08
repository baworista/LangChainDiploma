import json
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from typing import List
from graphSupervisor.state import OverallState, Perspectives, Analyst
from langchain.tools import tool
from langchain.agents import initialize_agent

# Аутентификация и инициализация LLM
load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Инструкции для создания аналитиков
analyst_instructions = """
You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:

First, review the provided research topic.

Next, create four AI analysts:
1. Human Resources Analyst, focusing on team dynamics and performance, team collaboration, and human trainings and development in the context of the topic.
2. Business Process Analyst, focusing on business process optimization, business process automation, and business process management in the context of the topic.
3. Knowledge Management Analyst, focusing on knowledge management processes, knowledge sharing, and knowledge tools in the context of the topic.
4. IT Systems Analyst, specializing in IT systems, IT tools, and IT strategies in the context of the topic.
"""

# Инструмент для создания аналитиков
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
    print("Raw output from structured_llm.invoke:", perspectives)

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

# Решение супервайзора
def supervisor_decision(state: OverallState) -> str:
    """
    Determines which analyst the supervisor should talk to next.
    """
    current_step = state.get("current_step", 0)
    max_steps = len(state.get("analysts", []))  # Используем длину списка аналитиков
    state["current_step"] = current_step + 1

    if current_step < max_steps:
        return state["analysts"][current_step]["name"]
    return END

# Запуск модели с инструментами
def invoke_model_with_tools(state: OverallState):
    """
    Invokes the model with the provided tools and updates the state.
    """
    tools = [create_analysts_tool]
    llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

    # Вызов инструмента для генерации аналитиков
    response = llm_with_tools.invoke(state["topic"])
    print("Response from llm with tools:", response.tool_calls)

    for tool_call in response.tool_calls:
        if tool_call["name"] == "create_analysts_tool":
            tool_response = create_analysts_tool(state["topic"])

            # Обновляем состояние аналитиков
            state["analysts"] = tool_response["analysts"]
    return state


# Пример использования
if __name__ == "__main__":
    # Инициализация состояния
    state = OverallState(
        topic="Digital Transformation in Organizations",
        questionnaire="Survey completed",
        analysts=[],
        analyst_progress={},
        aggregated_diagnosis=[],
        aggregated_recommendations=[],
        final_report=""
    )

    # Вызов модели с инструментами
    updated_state = invoke_model_with_tools(state)

    # Преобразование состояния для вывода
    state_dict = {
        "topic": updated_state["topic"],
        "analysts": updated_state["analysts"],
        "current_step": updated_state.get("current_step", 0),
    }

    # Вывод обновлённого состояния
    print("Updated OverallState:", json.dumps(state_dict, indent=4, ensure_ascii=False))
    print(updated_state)
