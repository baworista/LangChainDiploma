from graphSupervisor.state import AnalystState


def analyst_node(topic: str, name: str, role: str, description: str) -> AnalystState:
    """
    Processes an individual analyst and generates their unique AnalystState.

    Args:
        topic (str): The topic of the analysis.
        name (str): The name of the analyst.
        role (str): The role of the analyst.
        description (str): The description of the analyst's focus and tasks.

    Returns:
        AnalystState: The unique state for the processed analyst.
    """
    print(f"Processing {name}...")
    print(f"Name: {name}")
    print(f"Topic: {topic}")
    print(f"Role: {role}")
    print(f"Description: {description}")

    # Create and return the unique AnalystState
    analyst_state = {
        "analyst_name": name,
        "topic": topic,
        "role": role,
        "description": description,
    }

    print(f"Generated state for {name}:\n{analyst_state}")
    return analyst_state


