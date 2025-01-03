import json
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from graphNetwork.nodes.initiate_func import initialize_agents_from_state
from graphNetwork.nodes.react_agent_node import call_agent
from graphNetwork.nodes.report_writer_node import report_writer
from graphNetwork.states import OverallState

load_dotenv()
llm = ChatOpenAI(model_name=os.getenv("MODEL"))

# Создаем подграф для взаимодействия агентов
app_builder = StateGraph(OverallState)

# Определяем агентов
agents = {
    "HR_Agent": call_agent,
    "BP_Agent": call_agent,
    "IT_Agent": call_agent,
    "KM_Agent": call_agent,
}

for agent_name, agent_function in agents.items():
    app_builder.add_node(agent_name, agent_function)

# Создаем связи между агентами (каждый может общаться с каждым)
for agent_from in agents.keys():
    for agent_to in agents.keys():
        if agent_from != agent_to:  # Исключаем самих себя
            app_builder.add_edge(agent_from, agent_to)

# Добавляем стартовый узел
app_builder.add_conditional_edges(START, initialize_agents_from_state, [agents.items()], "Report_Writer")

app_builder.add_node("Report_Writer", report_writer)
app_builder.add_edge("Report_Writer", END)

# Компилируем основной граф
graphNetwork = app_builder.compile()

# Генерация Mermaid-графа с улучшенным расположением и цветами
graph_image = graphNetwork.get_graph(
    xray=1,
).draw_mermaid_png()

# Сохранение графа
with open("network_graph_diagram.png", "wb") as file:
    file.write(graph_image)
print("Network graph diagram saved as 'network_graph_diagram.png'")

# Thread configuration and graph input
thread = {"configurable": {"thread_id": "1"}}

# Load from file
with open("../data/answer_1.json", "r") as file:
    data = json.load(file)

user_input = {
    "topic": "Help a multinational manufacturing company in their journey to product management maturity.",
    "questionnaire" :  data
}

response = graphNetwork.invoke(user_input, thread)

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