import json
from langgraph.constants import START
from langgraph.graph import StateGraph
import subprocess
from langgraph.prebuilt import ToolNode

from graphHierarchicalTeams.nodes.supervisor import *
from graphHierarchicalTeams.nodes.report_writer_node import *
from graphHierarchicalTeams.nodes.subordinate_node import *
from graphHierarchicalTeams.nodes.team_node import *
from graphHierarchicalTeams.states import *


def create_team_builder():
    """
    Creates a graph for a team with an analyst and a reviewer.
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
    Creates a graph for a process with subteams.

    :param process_name: Process name (e.g., "Inside_Processes").
    :param subteams: Teams list (e.g., ["HR", "BP", "KM", "IT"]).
    """
    builder = StateGraph(SubordinateState)
    builder.add_node(f"{process_name}_Supervisor", subordinate_node)
    builder.add_node(f"Report_Writer", report_writer_node)

    # Add teams
    for team in subteams:
        team_builder = create_team_builder()
        builder.add_node(f"{team}_Team", team_builder.compile())
        builder.add_edge(f"{team}_Team", f"{process_name}_Supervisor")

    # Set the starting point
    builder.add_edge(START, f"{process_name}_Supervisor")

    # Add conditional edges
    builder.add_conditional_edges(f"{process_name}_Supervisor", subordinate_define_edge,
                                  [f"{team}_Team" for team in subteams] +
                                  [f"Report_Writer", END])

    # Link with Report Writer
    builder.add_edge(f"Report_Writer", f"{process_name}_Supervisor")

    return builder


def create_main_graph(processes):
    """
    Creates a graph for the main process with subteams.

    :param processes: Process and teams dictionary.
                      Example: {"Inside_Processes": ["HR", "BP", "KM", "IT"],
                               "Outside_Processes": ["Marketing", "Finance", "Legal",
                                                     "Customer_Support", "R&D"]}.
    """
    builder = StateGraph(OverallState)
    builder.add_node("Main_Supervisor", superivisor_node)
    tool_node = ToolNode([report_writer_tool])
    builder.add_node("Main_Report_Writer", tool_node)

    # Add processes
    for process_name, subteams in processes.items():
        process_team_builder = create_process_team_builder(process_name, subteams)
        builder.add_node(f"{process_name}_Team", process_team_builder.compile())
        builder.add_edge(f"{process_name}_Team", "Main_Supervisor")

    # Set the starting point
    builder.add_edge(START, "Main_Supervisor")

    # Add conditional edges
    builder.add_conditional_edges("Main_Supervisor", supervisor_define_edge,
                                  [f"{process_name}_Team" for process_name in processes.keys()] +
                                  ["Main_Report_Writer", END])

    # Link with Report Writer
    builder.add_edge("Main_Report_Writer", "Main_Supervisor")

    return builder


# Define processes and their teams
processes = {
    "Inside_Processes": ["HR", "BP", "KM", "IT"],
    "Outside_Processes": ["Marketing", "Finance", "Legal", "Customer_Support", "R&D"]
}

# Create the main graph
app_builder = create_main_graph(processes)

# Compile the graph
graphHierarchical = app_builder.compile()


# Get the Mermaid code
graph_object = graphHierarchical.get_graph(xray=2)
mermaid_code = graph_object.draw_mermaid()

# Save Mermaid code to file
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
    "questionnaire" : data
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
