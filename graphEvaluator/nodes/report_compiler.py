import os
from typing import List

from graphEvaluator.states import OverallState


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

    # Step 1: Load the reports
    reports_dict = load_reports(architecture_names)

    # Step 2: Create a dictionary with architecture name, simple anonymized name, and report
    compiled_reports = {}

    for i, (arch, report) in enumerate(reports_dict.items()):
        anonymized_name = f"Report_{i + 1}"
        compiled_reports[arch] = {
            "real_name": arch,
            "anonymized_name": anonymized_name,
            "report": report
        }

    # Step 3: Update the state with the compiled reports
    state.update({"reports": compiled_reports})
    return state