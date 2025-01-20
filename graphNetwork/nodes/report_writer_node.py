import os

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from graphNetwork.prompts.generators import create_summary_agent_prompt
from graphNetwork.states import OveralState

llm = ChatOpenAI(model=os.getenv("MODEL_SUPERVISOR"))

def report_writer_node(state: OveralState):
    """ Node to summarize diagnosis and recommendations in a single report"""

    print("... Write Report ...")


    # Generate question
    system_message = create_summary_agent_prompt(state)
    report = llm.invoke([SystemMessage(content=system_message)])

    print(f"Report: {report.content}")

    # Write messages to state
    return {"final_report": report}