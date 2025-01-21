import json

from langgraph.constants import END
from langgraph.graph import StateGraph

from graphEvaluator.nodes.comprehensive_evaluator import comprehensive_evaluator_node
from graphEvaluator.nodes.final_evaluator import final_evaluator_node
from graphEvaluator.nodes.g_evaluator import g_eval_evaluator_node
from graphEvaluator.nodes.individual_evaluator import individual_evaluator_node
from graphEvaluator.nodes.report_compiler import report_compiler_node
from graphEvaluator.states import OverallState

app_builder = StateGraph(OverallState)

app_builder.add_node("Report_Compiler", report_compiler_node)
app_builder.add_node("Comprehensive_Evaluator", comprehensive_evaluator_node)
app_builder.add_node("G-Eval_Node", g_eval_evaluator_node)
app_builder.add_node("Individual_Evaluator", individual_evaluator_node)
app_builder.add_node("Final_Evaluator", final_evaluator_node)

app_builder.set_entry_point("Report_Compiler")
app_builder.add_edge("Report_Compiler", "Comprehensive_Evaluator")
app_builder.add_edge("Report_Compiler", "Individual_Evaluator")
app_builder.add_edge("Report_Compiler", "G-Eval_Node")

app_builder.add_edge("Comprehensive_Evaluator", "Final_Evaluator")
app_builder.add_edge("G-Eval_Node", "Final_Evaluator")
app_builder.add_edge("Individual_Evaluator", "Final_Evaluator")

app_builder.add_edge("Final_Evaluator", END)

# Compile the graph
graphEvaluator = app_builder.compile()



graph_image = graphEvaluator.get_graph(xray=1).draw_mermaid_png()
with open("evaluator_graph_diagram.png", "wb") as file:
    file.write(graph_image)
print("Saved as PNG 'evaluator_graph_diagram.png'")


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
the_best_report = response.get("the_best_report_info")

if the_best_report:
    # Extract content from the The best report
    report_content = the_best_report.content

    # Define the output file path
    output_file_path = "the_best_report_info.md"

    # Write the report content to the output.md file
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(report_content)

    print(f"The best report has been written to {output_file_path}")
else:
    print("The best report is missing.")
