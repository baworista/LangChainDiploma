from langgraph.constants import START, END
from langgraph.graph import StateGraph

from graphSupervisor.nodes.analyst import *
from graphSupervisor.nodes.supervisor import supervisor_node
from graphSupervisor.state import OverallState

load_dotenv()

model = ChatOpenAI(temperature=0.0, model_name="gpt-4o-mini")


# Define simple testfiles functions for nodes
def testAnalyst(state):
    print(f"Function call for {state.get('node_name', 'unknown node')}")
    return state  # Return the same state for simplicity


# Build the graph
app_builder = StateGraph(OverallState)

# Add nodes
app_builder.add_node("supervisor", supervisor_node)
# app_builder.add_node("supervisor_tools", ToolNode([create_analysts_tool])) - additional for graph visualizing

# Set start and end points
app_builder.add_edge(START, 'supervisor')
app_builder.add_edge('supervisor', END)

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
