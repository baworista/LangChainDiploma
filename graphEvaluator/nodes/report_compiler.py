"""
Module for compiling and loading reports in a multi-agent system.

This module provides functionality to load reports from specified architectures,
assign anonymized names, and update the system state for further processing.

Functionality:
    - Loads reports from file paths based on architecture names.
    - Compiles the reports into a dictionary with anonymized names.
    - Updates the system state to include the compiled reports.

Dependencies:
    - `os`: For handling file paths and checking file existence.
    - `graphEvaluator.states.OverallState`: Defines the state structure for managing the workflow.

Functions:
    - `load_reports`: Loads reports from specified architectures into a dictionary.
    - `report_compiler_node`: Compiles reports, assigns anonymized names, and updates the state.
"""

import os
from typing import List

from graphEvaluator.states import OverallState


# Function to load reports into a dictionary
def load_reports(architectures: List[str]) -> dict[str, str]:
    """
    Load reports from the specified architectures into a dictionary.

    Args:
        architectures (List[str]): List of architecture names representing different report sources.

    Returns:
        dict[str, str]: A dictionary where keys are architecture names and values are the report content.

    Example:
        architectures = ["Architecture1", "Architecture2"]
        reports = load_reports(architectures)
        print(reports)
    """
    reports = {}
    for arch in architectures:
        report_path = os.path.join(f"../graph{arch}", f"output{arch}.md")
        if os.path.exists(report_path):
            print("The", f"graph{arch}", "report downloaded!")
            with open(report_path, "r") as file:
                reports[arch] = file.read()
        else:
            print(f"Warning: Report for {arch} not found at {report_path}")
    return reports


def report_compiler_node(state: OverallState):
    """
    Compile reports into a dictionary with anonymized names and updates the system state.

    Args:
        state (OverallState): Current system state containing:
            - reports (list): List of architecture names to load reports from.

    Returns:
        OverallState: Updated state with compiled reports, including:
            - "real_name": Original architecture name.
            - "anonymized_name": Anonymized name for the report.
            - "report": Report content.

    Example:
        state = {
            "reports": ["Architecture1", "Architecture2"]
        }
        updated_state = report_compiler_node(state)
        print(updated_state["reports"])
    """
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