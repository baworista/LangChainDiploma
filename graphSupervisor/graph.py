"""
Module for building and executing a supervisor workflow for a supervisor-led research process.

This module uses LangGraph to create a supervisor state graph consisting of teams (analyst and reviewer)
and supervisory nodes. The workflow facilitates generating structured analyses, reviews, and a final executive report.

Key Features:
- Define subgraphs for individual research teams.
- Build a supervisor state graph connecting teams and the supervisor.
- Generate a visual representation of the state graph as a PNG file.
- Execute the state graph to process user input and produce a final report.

Modules Used:
    - json: For handling JSON data.
    - langgraph.constants: Provides constants like START and END for defining graph transitions.
    - langgraph.graph: Core library for creating and managing state graphs.
    - graphSupervisor.nodes: Custom nodes for supervisor, report writer, and team roles.
    - graphSupervisor.states: Custom states for the overall and team-specific workflows.
    - dotenv: For loading environment variables.
    - langchain_openai: For interacting with OpenAI's language models.

Functions:
    - create_team_builder: Creates a state graph for a single research team (analyst and reviewer).

Graph Workflow:
1. **Supervisor Node:** Initializes the workflow, assigns teams, and monitors progress.
2. **Team Nodes:** Each team node alternates between analyst and reviewer roles until conditions are met.
3. **Report Writer Node:** Consolidates team outputs into a final report.

Outputs:
- Mermaid diagram saved as a PNG file (`supervisor_graph_diagram.png`).
- Final report generated from the workflow and saved as `outputSupervisor.md`.
"""

import json
from langgraph.constants import START
from langgraph.graph import StateGraph

from graphSupervisor.nodes.report_writer_node import *
from graphSupervisor.nodes.supervisor_node import *
from graphSupervisor.nodes.team_node import *
from graphSupervisor.states import *


load_dotenv()
model = ChatOpenAI(temperature=0.1, model_name="gpt-4o-mini")


# Define subgraphs
def create_team_builder():
    """
    Create a state graph for a single research team.

    Each team alternates between two roles:
    - Analyst: Performs needs analysis based on questionnaire results.
    - Reviewer: Provides constructive feedback on the analyst's analysis.

    Edges:
    - START -> Analyst
    - Analyst -> Reviewer or END (conditional)
    - Reviewer -> Analyst

    Returns:
        StateGraph: A compiled state graph for a single research team.
    """
    team_builder = StateGraph(ResearchState)
    team_builder.add_node("Analyst", analyst_node)
    team_builder.add_node("Reviewer", reviewer_node)

    team_builder.add_edge(START, "Analyst")

    team_builder.add_conditional_edges("Analyst", should_continue, ["Reviewer", END])
    team_builder.add_edge("Reviewer", "Analyst")
    return team_builder


hr_team_builder = create_team_builder()
bp_team_builder = create_team_builder()
km_team_builder = create_team_builder()
it_team_builder = create_team_builder()

app_builder = StateGraph(OverallState)

app_builder.add_node("Supervisor", supervisor_node)
app_builder.add_node("Report_Writer", report_writer_node)

app_builder.add_node("HR_Team", hr_team_builder.compile())
app_builder.add_node("BP_Team", bp_team_builder.compile())
app_builder.add_node("KM_Team", km_team_builder.compile())
app_builder.add_node("IT_Team", it_team_builder.compile())


# Build the main graph
app_builder.add_edge(START, 'Supervisor')

app_builder.add_conditional_edges('Supervisor', define_edge,
                                  ["HR_Team", "BP_Team", "IT_Team", "KM_Team", "Report_Writer", END])

app_builder.add_edge('HR_Team', 'Supervisor')
app_builder.add_edge('BP_Team', 'Supervisor')
app_builder.add_edge('KM_Team', 'Supervisor')
app_builder.add_edge('IT_Team', 'Supervisor')
app_builder.add_edge('Report_Writer', 'Supervisor')

app = app_builder.compile()

# Compile the graph
graphSupervisor = app_builder.compile()

# Save as PNG
graph_image = graphSupervisor.get_graph(xray=1).draw_mermaid_png()
with open("supervisor_graph_diagram.png", "wb") as file:
    file.write(graph_image)
print("Saved as PNG 'supervisor_graph_diagram.png'")


# Thread configuration and graph input
thread = {"configurable": {"thread_id": "1"}}

# Load from file
with open("../data/answer_1.json", "r") as file:
    data = json.load(file)

user_input = {
    "topic": "Help a multinational manufacturing company in their journey to product management maturity.",
    "questionnaire" :  data
}

response = graphSupervisor.invoke(user_input, thread)

# Assuming the response is already generated
final_report = response.get("final_report")

if final_report:
    # Extract content from the final report
    report_content = final_report.content

    # Define the output file path
    output_file_path = "outputSupervisor.md"

    # Write the report content to the outputSupervisor.md file
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(report_content)

    print(f"Final report has been written to {output_file_path}")
else:
    print("Final report is missing.")
