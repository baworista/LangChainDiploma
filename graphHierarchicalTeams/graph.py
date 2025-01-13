import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.constants import START
from langgraph.graph import StateGraph
import subprocess
from graphHierarchicalTeams.nodes.supervisor import *
from graphHierarchicalTeams.nodes.report_writer_node import *
from graphHierarchicalTeams.nodes.subordinate_node import *
from graphHierarchicalTeams.nodes.team_node import *
from graphHierarchicalTeams.states import *

load_dotenv()
model = ChatOpenAI(temperature=0.1, model_name="gpt-4o-mini")

def test_node(state: OverallState):
    print("Test Node")
    return state


def create_team_builder():
    """
    Создаёт граф команды с аналитиком и рецензентом.
    """
    team_builder = StateGraph(ResearchState)
    team_builder.add_node(f"Analyst", analyst_node)
    team_builder.add_node(f"Reviewer", reviewer_node)

    team_builder.add_edge(START, f"Analyst")
    team_builder.add_conditional_edges(f"Analyst", should_continue,
                                       [f"Reviewer", END])
    team_builder.add_edge(f"Reviewer", f"Analyst")
    return team_builder


def create_process_team_builder(process_name, subteams):
    """
    Создаёт граф для процесса с заданными командами.

    :param process_name: Название процесса (например, "Inside_Processes").
    :param subteams: Список названий команд (например, ["HR", "BP", "KM", "IT"]).
    """
    builder = StateGraph(SubordinateState)
    builder.add_node(f"{process_name}_Supervisor", subordinate_node)
    builder.add_node(f"Report_Writer", test_node)

    # Добавляем команды
    for team in subteams:
        team_builder = create_team_builder()
        builder.add_node(f"{team}_Team", team_builder.compile())
        builder.add_edge(f"{team}_Team", f"{process_name}_Supervisor")

    # Указываем начальную точку
    builder.add_edge(START, f"{process_name}_Supervisor")

    # Добавляем условные связи
    builder.add_conditional_edges(f"{process_name}_Supervisor", subordinate_define_edge,
                                  [f"{team}_Team" for team in subteams] +
                                  [f"Report_Writer", END])

    # Связь с Report Writer
    builder.add_edge(f"Report_Writer", f"{process_name}_Supervisor")

    return builder


def create_main_graph(processes):
    """
    Создаёт основной граф с заданными процессами.

    :param processes: Словарь с процессами и их командами.
                      Пример: {"Inside_Processes": ["HR", "BP", "KM", "IT"],
                               "Outside_Processes": ["Marketing", "Finance", "Legal",
                                                     "Customer_Support", "R&D"]}.
    """
    builder = StateGraph(OverallState)
    builder.add_node("Main_Supervisor", superivisor_node)
    builder.add_node("Main_Report_Writer", test_node)

    # Добавляем процессы
    for process_name, subteams in processes.items():
        process_team_builder = create_process_team_builder(process_name, subteams)
        builder.add_node(f"{process_name}_Team", process_team_builder.compile())
        builder.add_edge(f"{process_name}_Team", "Main_Supervisor")

    # Указываем начальную точку
    builder.add_edge(START, "Main_Supervisor")

    # Добавляем условные связи
    builder.add_conditional_edges("Main_Supervisor", supervisor_define_edge,
                                  [f"{process_name}_Team" for process_name in processes.keys()] +
                                  ["Main_Report_Writer", END])

    # Связь с Report Writer
    builder.add_edge("Main_Report_Writer", "Main_Supervisor")

    return builder


# Задаём процессы и их команды
processes = {
    "Inside_Processes": ["HR", "BP", "KM", "IT"],
    "Outside_Processes": ["Marketing", "Finance", "Legal", "Customer_Support", "R&D"]
}

# Создаём основной граф
app_builder = create_main_graph(processes)

# Компилируем граф
graphHierarchical = app_builder.compile()


# Получаем Mermaid-код
graph_object = graphHierarchical.get_graph(xray=2)
mermaid_code = graph_object.draw_mermaid()

# Сохраняем Mermaid-код в файл
with open("whole_hierarchical_graph_diagram.mmd", "w") as file:
    file.write(mermaid_code)
print("Mermaid code saved as 'whole_hierarchical_graph_diagram.mmd'")

# Mermaid to PNG
subprocess.run(["mmdc", "-i", "whole_hierarchical_graph_diagram.mmd", "-o", "whole_hierarchical_graph_diagram.png", "-s", "5"])
print("PNG saved as 'whole_hierarchical_graph_diagram.png'")


# Thread configuration and graph input
thread = {"configurable": {"thread_id": "1"}}

# Load from file
with open("../data/answer_1.json", "r") as file:
    data = json.load(file)

user_input = {
    "topic": "Help a multinational manufacturing company in their journey to product management maturity.",
    "questionnaire" :  "Here should be the questionnaire results or user input. Now it's just a placeholder.",
}

response = graphHierarchical.invoke(user_input, thread)

# Assuming the response is already generated
final_report = response.get("final_report")

if final_report:
    # Extract content from the final report
    report_content = final_report.content

    # Define the output file path
    output_file_path = "output.md"

    # Write the report content to the output.md file
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(report_content)

    print(f"Final report has been written to {output_file_path}")
else:
    print("Final report is missing.")
