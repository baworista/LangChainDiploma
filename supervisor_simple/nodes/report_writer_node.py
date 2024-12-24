from supervisor_simple.states import OverallState


def report_writer(state: OverallState):
    topic = state["topic"]
    # prompt = f"You are tasked to summarize teams resolutions messages about this {topic}"
    print("report_writer node activated!!")
    print(len(state["reviews"]))
    return {"final_report": ["Good game"]}
