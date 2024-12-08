from langgraph.constants import START, END
from langgraph.graph import StateGraph
from graphSupervisor import state
from graphSupervisor.nodes.supervisor import supervisor_decision
from graphSupervisor.state import OverallState


# Define simple test functions for nodes
def testAnalyst(state):
    print(f"Function call for {state.get('node_name', 'unknown node')}")
    return state  # Return the same state for simplicity


# Build the graph
app_builder = StateGraph(OverallState)

# Add nodes
app_builder.add_node('supervisor', testAnalyst)  # Supervisor node
app_builder.add_node('HRAnalyst', testAnalyst)  # Human Resources Analyst
app_builder.add_node('BPAnalyst', testAnalyst)  # Business Process Analyst
app_builder.add_node('KMAnalyst', testAnalyst)  # Knowledge Management Analyst
app_builder.add_node('ITAnalyst', testAnalyst)  # IT System Analyst

# Add conditional edges for supervisor to talk to each analyst sequentially
app_builder.add_conditional_edges(
    'supervisor',  # Source node
    supervisor_decision,  # Decision-making function
    ['HRAnalyst', 'BPAnalyst', 'KMAnalyst', 'ITAnalyst', END]  # Target nodes
)

# Add edges for analysts to return to supervisor
app_builder.add_edge('HRAnalyst', 'supervisor')
app_builder.add_edge('BPAnalyst', 'supervisor')
app_builder.add_edge('KMAnalyst', 'supervisor')
app_builder.add_edge('ITAnalyst', 'supervisor')

# Set start and end points
app_builder.add_edge(START, 'supervisor')

# Compile the graph
graphSupervisor = app_builder.compile()

# Save as PNG
graph_image = graphSupervisor.get_graph().draw_mermaid_png()
with open("graph_diagram.png", "wb") as file:
    file.write(graph_image)
print("Saved as PNG 'graph_diagram.png'")
