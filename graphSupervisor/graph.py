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
    output_file_path = "output.md"

    # Write the report content to the output.md file
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(report_content)

    print(f"Final report has been written to {output_file_path}")
else:
    print("Final report is missing.")
