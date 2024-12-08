from langchain.agents import initialize_agent
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from nodes.analyst import analyst_node
from graphSupervisor import state
from graphSupervisor.nodes.supervisor import supervisor_decision, create_analysts_tool, supervisor_node
from graphSupervisor.state import OverallState, AnalystState

model = ChatOpenAI(temperature=0.0, model_name="gpt-4o-mini")


# Define simple test functions for nodes
def testAnalyst(state):
    print(f"Function call for {state.get('node_name', 'unknown node')}")
    return state  # Return the same state for simplicity


# Build the graph
app_builder = StateGraph(OverallState)

# Add nodes
app_builder.add_node('supervisor', supervisor_node)  # Supervisor node
# app_builder.add_node("supervisor_tools", ToolNode([create_analysts_tool])) - additional for graph visualizing

app_builder.add_node('HRAnalyst', lambda state: analyst_node(
    state["topic"],
    state["analysts"][0]["name"],
    state["analysts"][0]["role"],
    state["analysts"][0]["description"]
))  # Human Resources Analyst

app_builder.add_node('BPAnalyst', lambda state: analyst_node(
    state["topic"],
    state["analysts"][1]["name"],
    state["analysts"][1]["role"],
    state["analysts"][1]["description"]
))  # Business Process Analyst

app_builder.add_node('KMAnalyst', lambda state: analyst_node(
    state["topic"],
    state["analysts"][2]["name"],
    state["analysts"][2]["role"],
    state["analysts"][2]["description"]
))  # Knowledge Management Analyst

app_builder.add_node('ITAnalyst', lambda state: analyst_node(
    state["topic"],
    state["analysts"][3]["name"],
    state["analysts"][3]["role"],
    state["analysts"][3]["description"]
))  # IT Systems Analyst


# Add conditional edges for supervisor to talk to each analyst sequentially
app_builder.add_conditional_edges(
    'supervisor',  # Source node
    supervisor_decision,  # Decision-making function
    ['HRAnalyst', 'BPAnalyst', 'KMAnalyst', 'ITAnalyst', END]  # Target nodes
)

# Set start and end points
app_builder.add_edge(START, 'supervisor')

# Add edges for analysts to return to supervisor
app_builder.add_edge('HRAnalyst', 'supervisor')
app_builder.add_edge('BPAnalyst', 'supervisor')
app_builder.add_edge('KMAnalyst', 'supervisor')
app_builder.add_edge('ITAnalyst', 'supervisor')

# Compile the graph
graphSupervisor = app_builder.compile()

# Save as PNG
graph_image = graphSupervisor.get_graph().draw_mermaid_png()
with open("graph_diagram.png", "wb") as file:
    file.write(graph_image)
print("Saved as PNG 'graph_diagram.png'")


# Thread configuration and graph input
thread = {"configurable": {"thread_id": "1"}}

user_input = {
    "topic": "Help a multinational manufacturing company in their journey to product management maturity.",
}

# response = graph.invoke(user_input, thread)
#
# print(response)

# Stream through the graph with the user-defined task
for state in graphSupervisor.stream(user_input, thread):
    print("-" * 50)  # Separator for readability
    print("Current State (Raw):", state)  # Print the entire state for debugging

    # Extract the current node's state dynamically
    current_node_state = next(iter(state.values()))  # Get the first value from the dictionary

    # Safely access keys from the current node's state
    print("Processed State:")
    print(f"Topic: {current_node_state.get('topic', 'N/A')}")
    print("-" * 50)  # Separator for clarity
