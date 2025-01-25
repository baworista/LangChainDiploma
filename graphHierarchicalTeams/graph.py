"""
Module for creating and managing a hierarchical state graph for process-based team workflows.

This module uses `langgraph` to build and compile a hierarchical state graph for processes
involving analysts, reviewers, and supervisors. It facilitates the creation of subteams,
process teams, and the overall workflow for generating structured reports.

Key Features:
- Define team workflows for analysts and reviewers.
- Create process-specific graphs for subteams.
- Build and compile a main graph that integrates all processes.
- Generate a Mermaid diagram to visualize the state graph.
- Use a compiled graph to process user input and produce a final report.

Modules Used:
    - json: For loading and handling JSON data.
    - subprocess: For executing external commands (e.g., Mermaid CLI).
    - langgraph: For managing state graphs and nodes.
    - graphHierarchicalTeams: Custom module for nodes and states.

Functions:
    - create_team_builder: Creates a state graph for an individual team (analyst and reviewer).
    - create_process_team_builder: Creates a graph for a process with multiple subteams.
    - create_main_graph: Builds the main hierarchical graph for all processes.
"""

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
    Create a graph for a team with an analyst and a reviewer.

    The team builder defines a workflow where the analyst performs a needs analysis,
    and the reviewer provides feedback. The workflow alternates between these roles until
    a defined condition is met.

    Returns:
        StateGraph: A compiled state graph for the team workflow.
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
    Create a graph for a process with subteams.

    Each subteam has its own workflow (analyst and reviewer), and the process supervisor
    orchestrates the overall process.

    Args:
        process_name (str): The name of the process (e.g., "Inside_Processes").
        subteams (list): A list of subteam names (e.g., ["HR", "BP", "KM", "IT"]).

    Returns:
        StateGraph: A compiled state graph for the process.
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
    Create a graph for the main hierarchical process with multiple processes and their subteams.

    The main graph integrates all process-specific graphs and adds a main supervisor node
    for overall orchestration.

    Args:
        processes (dict): A dictionary where keys are process names and values are lists of subteam names.
            Example::

                {
                    "Inside_Processes": ["HR", "BP", "KM", "IT"],
                    "Outside_Processes": ["Marketing", "Finance", "Legal", "Customer_Support", "R&D"]
                }

    Returns:
        StateGraph: A compiled state graph for the entire hierarchical process.
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
    output_file_path = "outputHierarchicalTeams.md"

    # Write the report content to the outputHierarchicalTeams.md file
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(report_content)

    print(f"Final report has been written to {output_file_path}")
else:
    print("Final report is missing.")

# Additional Details:
# - The compiled graph is visualized as a Mermaid diagram and saved as a PNG.
# - The hierarchical workflow processes user input to generate a final structured report.
# - The final report is saved as `outputHierarchicalTeams.md` if generated successfully.
