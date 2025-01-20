import json
import subprocess

from langgraph.constants import END
from langgraph.graph import StateGraph

from graphEvaluator.nodes.comprehensive_evaluator import comprehensive_evaluator_node
from graphEvaluator.nodes.individual_evaluator import individual_evaluator_node
from graphEvaluator.nodes.report_compiler import report_compiler_node
from graphEvaluator.nodes.states import OverallState


app_builder = StateGraph(OverallState)

app_builder.add_node("Report_Compiler", report_compiler_node)
# app_builder.add_node("Comprehensive_Evaluator", comprehensive_evaluator_node)
app_builder.add_node("Individual_Evaluator", individual_evaluator_node)

app_builder.set_entry_point("Report_Compiler")
# app_builder.add_edge("Report_Compiler", "Comprehensive_Evaluator")
app_builder.add_edge("Report_Compiler", "Individual_Evaluator")

app_builder.add_edge("Individual_Evaluator", END)
# Compile the graph
graphEvaluator = app_builder.compile()






# Get the Mermaid code
graph_object = graphEvaluator.get_graph(xray=2)
mermaid_code = graph_object.draw_mermaid()

# Save Mermaid code to file
with open("evaluator_graph_diagram.mmd", "w") as file:
    file.write(mermaid_code)
print("Mermaid code saved as 'evaluator_graph_diagram.mmd'")

# Mermaid to PNG
subprocess.run(["mmdc", "-i", "evaluator_graph_diagram.mmd", "-o", "evaluator_graph_diagram.png", "-s", "5"])
print("PNG saved as 'evaluator_graph_diagram.png'")


# Thread configuration and graph input
thread = {"configurable": {"thread_id": "1"}}

# Load from file
with open("../data/answer_1.json", "r") as file:
    data = json.load(file)

user_input = {
    "topic": "Help a multinational manufacturing company in their journey to product management maturity.",
    "questionnaire" : data,
    "reports": ["Supervisor", "Network", "HierarchicalTeams"]
}

response = graphEvaluator.invoke(user_input, thread)

# Assuming the response is already generated
the_best_report = response.get("the_best_report")

if the_best_report:
    # Extract content from the The best report
    report_content = the_best_report.content

    # Define the output file path
    output_file_path = "the_best_report.md"

    # Write the report content to the output.md file
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(report_content)

    print(f"The best report has been written to {output_file_path}")
else:
    print("The best report is missing.")
