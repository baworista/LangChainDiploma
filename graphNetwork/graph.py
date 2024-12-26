import os
from dotenv import load_dotenv
from langchain.agents import create_react_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from graphNetwork.schemas import Response
from graphNetwork.states import OverallState

load_dotenv()
llm = ChatOpenAI(model_name=os.getenv("MODEL"))

def reActAgent(state: OverallState):
    tools = []
    prompt = ""
    structured_llm = llm.with_structured_output(Response)
    agent = create_react_agent(tools=tools, llm=llm, prompt=prompt)

    # Логика агента (добавьте взаимодействие с LLM здесь)
    pass

# Инициализация агентов
def initialize_agents(state: OverallState):
    # Здесь можно добавить логику инициализации агентов
    pass

# Финальный сбор отчета
def report_writer(state: OverallState):
    # Сбор и вывод финального результата
    pass



# Создаем подграф для взаимодействия агентов
app_builder = StateGraph(OverallState)

# Определяем агентов
agents = {
    "HR_Team": reActAgent,
    "BP_Team": reActAgent,
    "IT_Team": reActAgent,
    "KM_Team": reActAgent
}

# Добавляем узлы для агентов
for agent_name, agent_function in agents.items():
    app_builder.add_node(agent_name, agent_function)

# Создаем связи между агентами (каждый может общаться с каждым)
for agent_from in agents.keys():
    for agent_to in agents.keys():
        if agent_from != agent_to:  # Исключаем самих себя
            app_builder.add_edge(agent_from, agent_to)

# Добавляем стартовый узел
app_builder.add_conditional_edges(START, initialize_agents, [agents.items()], "Report_Writer")

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