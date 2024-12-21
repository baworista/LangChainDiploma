from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.constants import START
from langgraph.graph import StateGraph

from nodes.supervisor_node import supervisor_node, initialize_research_states
from nodes.team_node import *
from supervisor_simple.states import *

load_dotenv()
model = ChatOpenAI(temperature=0.1, model_name="gpt-4o-mini")

# Define subgraphs
hr_team_builder = StateGraph(ResearchState)

hr_team_builder.add_node("Analyst", analyst_node)
hr_team_builder.add_node("Reviewer", reviewer_node)
hr_team_builder.set_entry_point("Analyst")

hr_team_builder.add_edge("Analyst", "Reviewer")
hr_team_builder.add_conditional_edges("Reviewer", should_continue)

bp_team_builder = StateGraph(ResearchState)

bp_team_builder.add_node("Analyst", analyst_node)
bp_team_builder.add_node("Reviewer", reviewer_node)
bp_team_builder.set_entry_point("Analyst")

bp_team_builder.add_edge("Analyst", "Reviewer")
bp_team_builder.add_conditional_edges("Reviewer", should_continue)

km_team_builder = StateGraph(ResearchState)

km_team_builder.add_node("Analyst", analyst_node)
km_team_builder.add_node("Reviewer", reviewer_node)
km_team_builder.set_entry_point("Analyst")

km_team_builder.add_edge("Analyst", "Reviewer")
km_team_builder.add_conditional_edges("Reviewer", should_continue)

it_team_builder = StateGraph(ResearchState)

it_team_builder.add_node("Analyst", analyst_node)
it_team_builder.add_node("Reviewer", reviewer_node)
it_team_builder.set_entry_point("Analyst")

it_team_builder.add_edge("Analyst", "Reviewer")
it_team_builder.add_conditional_edges("Reviewer", should_continue)

app_builder = StateGraph(OverallState)

app_builder.add_node("Supervisor", supervisor_node)
app_builder.add_node("Report_Writer", reviewer_node)

app_builder.add_node("HR_Team", hr_team_builder.compile())
app_builder.add_node("BP_Team", bp_team_builder.compile())
app_builder.add_node("KM_Team", km_team_builder.compile())
app_builder.add_node("IT_Team", it_team_builder.compile())

# app_builder.add_node("supervisor_tools", ToolNode([create_analysts_tool])) - additional for graph visualizing

# Build the main graph
app_builder.add_edge(START, 'Supervisor')

# app_builder.add_edge('Supervisor', 'HR_Team')
# app_builder.add_edge('Supervisor', 'BP_Team')
# app_builder.add_edge('Supervisor', 'KM_Team')
# app_builder.add_edge('Supervisor', 'IT_Team')

app_builder.add_conditional_edges('Supervisor', initialize_research_states,
                                  ["HR_Team", "BP_Team", "KM_Team", "IT_Team"])

app_builder.add_edge('HR_Team', 'Supervisor')
app_builder.add_edge('BP_Team', 'Supervisor')
app_builder.add_edge('KM_Team', 'Supervisor')
app_builder.add_edge('IT_Team', 'Supervisor')

app_builder.add_edge('Supervisor', 'Report_Writer')  # wait for others(COMMAND)

app_builder.add_edge('Report_Writer', END)

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

user_input = {
    "topic": "Help a multinational manufacturing company in their journey to product management maturity.",
}

response = graphSupervisor.invoke(user_input, thread)
#
# print(response)

# # Stream through the graph with the user-defined task
# for state in graphSupervisor.stream(user_input, thread):
#     print("-" * 50)  # Separator for readability
#     print("Current State (Raw):", state)  # Print the entire state for debugging
#
#     # Extract the current node's state dynamically
#     current_node_state = next(iter(state.values()))  # Get the first value from the dictionary
#
#     # Safely access keys from the current node's state
#     print("Processed State:")
#     print(f"Topic: {current_node_state.get('topic', 'N/A')}")
#     print("-" * 50)  # Separator for clarity
