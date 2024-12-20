from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from nodes.supervisor_node import supervisor_node
from nodes.team_node import *
from states import *

load_dotenv()
model = ChatOpenAI(temperature=0.1, model_name="gpt-4o-mini")

# Build the graph
app_builder = StateGraph(OverallState)

# Add nodes
app_builder.add_node("Supervisor", supervisor_node)

app_builder.add_node("HR_Analyst", analyst_node)
app_builder.add_node("BP_Analyst", analyst_node)
app_builder.add_node("KM_Analyst", analyst_node)
app_builder.add_node("IT_Analyst", analyst_node)

app_builder.add_node("HR_Reviewer", reviewer_node)
app_builder.add_node("BP_Reviewer", reviewer_node)
app_builder.add_node("KM_Reviewer", reviewer_node)
app_builder.add_node("IT_Reviewer", reviewer_node)

app_builder.add_node("Report_Writer", reviewer_node)
# app_builder.add_node("supervisor_tools", ToolNode([create_analysts_tool])) - additional for graph visualizing

# Set start and end points
app_builder.add_edge(START, 'Supervisor')

app_builder.add_edge('Supervisor', 'HR_Analyst')
app_builder.add_edge('Supervisor', 'BP_Analyst')
app_builder.add_edge('Supervisor', 'KM_Analyst')
app_builder.add_edge('Supervisor', 'IT_Analyst')

app_builder.add_edge('HR_Analyst', 'HR_Reviewer')
app_builder.add_edge('BP_Analyst', 'BP_Reviewer')
app_builder.add_edge('KM_Analyst', 'KM_Reviewer')
app_builder.add_edge('IT_Analyst', 'IT_Reviewer')

app_builder.add_conditional_edges('HR_Reviewer', if_continue_conversation, ['HR_Analyst', 'Supervisor'])
app_builder.add_conditional_edges('BP_Reviewer', if_continue_conversation, ['BP_Analyst', 'Supervisor'])
app_builder.add_conditional_edges('KM_Reviewer', if_continue_conversation, ['KM_Analyst', 'Supervisor'])
app_builder.add_conditional_edges('IT_Reviewer', if_continue_conversation, ['IT_Analyst', 'Supervisor'])

app_builder.add_edge('Supervisor', 'Report_Writer')

app_builder.add_edge('Report_Writer', END)

# Compile the graph
graphSupervisor = app_builder.compile()

# Save as PNG
graph_image = graphSupervisor.get_graph().draw_mermaid_png()
with open("supervisor_graph_diagram.png", "wb") as file:
    file.write(graph_image)
print("Saved as PNG 'supervisor_graph_diagram.png'")

# Thread configuration and graph input
thread = {"configurable": {"thread_id": "1"}}

user_input = {
    "topic": "Help a multinational manufacturing company in their journey to product management maturity.",
}

# response = graphSupervisor.invoke(user_input, thread)
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
