import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from graphNetwork.nodes.initiate_func import initialize_agents_from_state
from graphNetwork.nodes.react_agent_node import reActAgent
from graphNetwork.nodes.report_writer_node import report_writer
from graphNetwork.states import OverallState

load_dotenv()
llm = ChatOpenAI(model_name=os.getenv("MODEL"))

# Создаем подграф для взаимодействия агентов
app_builder = StateGraph(OverallState)

# Определяем агентов
agents = {
    "HR_Agent": reActAgent,
    "BP_Agent": reActAgent,
    "IT_Agent": reActAgent,
    "KM_Agent": reActAgent,
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
network = app_builder.compile()

# Генерация Mermaid-графа с улучшенным расположением и цветами
graph_image = network.get_graph(
    xray=1,
).draw_mermaid_png()

# Сохранение графа
with open("network_graph_diagram.png", "wb") as file:
    file.write(graph_image)
print("Network graph diagram saved as 'network_graph_diagram.png'")