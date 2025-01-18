import json

from langgraph.constants import END, START
from langgraph.graph import StateGraph

from graphNetwork.nodes.agent_nodes import *
from graphNetwork.nodes.evaluator import evaluate_with_gpt4
from graphNetwork.nodes.report_writer_node import report_writer_node
from graphNetwork.states import OveralState

DATA_PATH = "../data/"

def load_json(filename):
    with open(f"{DATA_PATH}{filename}", 'r', encoding='utf-8') as f:
        return json.load(f)

questionare = load_json("answer_1.json")
good_practices = load_json("good_practices.json")

# Build the state graph
builder = StateGraph(OveralState)
builder.add_node("Consulting_Agent", Consulting_Agent)
builder.add_node("HR_Agent", HR_Agent)
builder.add_node("BP_Agent", BP_Agent)
builder.add_node("KM_Agent", KM_Agent)
builder.add_node("IT_Agent", IT_Agent)
builder.add_node("Summary_Agent", report_writer_node)
builder.add_node("Evaluator_Agent", evaluate_with_gpt4)

builder.add_edge(START, "Consulting_Agent")
builder.add_edge("Summary_Agent", "Evaluator_Agent")
builder.add_edge("Evaluator_Agent", END)

graphNetwork = builder.compile()

# Execute the graph
initial_state = {
    "main_task": "Help multinational corporation with filled questionnaire in digital transformation using provided questionare from corporation and good practices. Diagnose and give some recommendations.",
    "questionare": questionare,
    "good_practices": good_practices,
}

graphNetwork.invoke(initial_state)

graph_image = graphNetwork.get_graph(xray=1).draw_mermaid_png()
with open("network_graph_diagram.png", "wb") as file:
    file.write(graph_image)
print("Saved as PNG 'network_graph_diagram.png'")