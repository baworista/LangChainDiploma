import json

from langgraph.constants import END, START
from langgraph.graph import StateGraph

from graphNetwork.nodes.agent_nodes import *
from graphNetwork.nodes.report_writer_node import report_writer_node
from graphNetwork.states import OveralState

DATA_PATH = "../data/"

def load_json(filename):
    with open(f"{DATA_PATH}{filename}", 'r', encoding='utf-8') as f:
        return json.load(f)

questionnaire = load_json("answer_1.json")
good_practices = load_json("good_practices.json")

# Build the state graph
builder = StateGraph(OveralState)
builder.add_node("Consulting_Agent", Consulting_Agent)

builder.add_node("HR_Agent", HR_Agent)
builder.add_node("BP_Agent", BP_Agent)
builder.add_node("KM_Agent", KM_Agent)
builder.add_node("IT_Agent", IT_Agent)

builder.add_node("Summary_Agent", report_writer_node)

builder.add_edge(START, "Consulting_Agent")
builder.add_edge("Summary_Agent", END)
graphNetwork = builder.compile()

graph_image = graphNetwork.get_graph(xray=1).draw_mermaid_png()
with open("network_graph_diagram.png", "wb") as file:
    file.write(graph_image)
print("Saved as PNG 'network_graph_diagram.png'")

# Thread configuration and graph input
thread = {"configurable": {"thread_id": "1"}}

# Load from file
with open("../data/answer_1.json", "r") as file:
    data = json.load(file)

# Load from file
with open("../data/good_practices.json", "r") as file:
    gp = json.load(file)

user_input = {
    "main_task": "Help a multinational manufacturing company in their journey to product management maturity.",
    "questionnaire" : data,
    "good_practices": gp
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





