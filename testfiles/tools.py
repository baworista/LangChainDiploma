import json
import os
from typing import List
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import Send

from graphSupervisor.states import OverallState, Perspectives


@tool
def write_report(reviews):
    """
    Tool to write review based on teams answers
    """
    # prompt = f"You are tasked to summarize teams resolutions messages about this {topic}"
    print("report_writer node activated!!")
    print(len(state["reviews"]))
    return {"final_report": ["Good game"]}


@tool
def initialize_research_states(state: OverallState) -> list[Send]:
    """
    Initializes states for each research team and executes subgraphs.
    If no teams exist in the state, generates them using an LLM.
    """
    # Если в состоянии нет команд, создаём их
    if "teams" not in state or not state["teams"]:
        print(f"Creating research teams for topic: \n\t{state['topic']}")
        structured_llm = llm.with_structured_output(Perspectives)

        # LLM Query для генерации команд
        system_message = SystemMessage(content=team_creation_instructions)
        human_message = HumanMessage(content=f"Generate the teams for the topic: {state['topic']}.")

        # Генерация команд
        perspectives: Perspectives = structured_llm.invoke([system_message, human_message])
        state["teams"] = [
            {
                "name": team.name,
                "description": team.description,
                "analyst_prompt": team.analyst_prompt,
                "reviewer_prompt": team.reviewer_prompt,
            }
            for team in perspectives.teams
        ]
        print("Teams successfully created.")

    # Отображаем количество собранных результатов
    print("Number of teams results from supervisor_node:")
    print(len(state.get("reviewer_final_overview", [])))

    topic = state["topic"]
    teams = state["teams"]
    print(f"Initializing research teams for topic: \n\t{topic}")

    # Создаём задачи для отправки в сабграфы
    return [
        Send(
            team["name"],
            {
                "topic": topic,
                "description": team["description"],
                "questionnaire": "=====",
                "analyst_prompt": team["analyst_prompt"],
                "reviewer_prompt": team["reviewer_prompt"],
            },
        )
        for team in teams
    ]