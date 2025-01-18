import os
from platform import architecture
from typing import List

from langchain.tools import tool

from graphEvaluator.nodes.states import OverallState


# Function to load reports into a dictionary
def load_reports(architectures: List[str]) -> dict[str, str]:
    """
    Load reports into a dictionary from the specified architectures

    :param: list of architecture names:
    :return: dictionary of reports
    """
    reports = {}
    for arch in architectures:
        report_path = os.path.join(f"../graph{arch}", "output.md")
        if os.path.exists(report_path):
            print("The", f"graph{arch}", "report downloaded!")
            with open(report_path, "r") as file:
                reports[arch] = file.read()
        else:
            print(f"Warning: Report for {arch} not found at {report_path}")
    return reports


def report_compiler_node(state: OverallState):
    print("Report Compiler activated.")

    architecture_names = state["reports"]
    print(architecture_names)
    reports_dict = load_reports(architecture_names)
    state.update({"reports": reports_dict})
    return state