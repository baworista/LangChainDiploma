"""
Module for compiling and loading reports in a multi-agent system.

This module defines functions to load reports from specified architectures, compile them into a
dictionary with anonymized names, and update the system state. The compiled reports are used for
evaluation and further processing.

Functions:
    - load_reports: Loads reports from file paths corresponding to specified architecture names.
    - report_compiler_node: Compiles reports, assigns anonymized names, and updates the system state.

Dependencies:
    - os: For file path handling and checking file existence.
    - graphEvaluator.states.OverallState: Defines the state structure for the multi-agent workflow.

Functions:
    def load_reports(architectures: List[str]) -> dict[str, str]:
        Loads reports into a dictionary from specified architectures.

        Args:
            architectures (List[str]): List of architecture names representing different report sources.

        Returns:
            dict[str, str]: A dictionary where keys are architecture names and values are the report content.

        Example:
            architectures = ["Architecture1", "Architecture2"]
            reports = load_reports(architectures)
            print(reports)

        Output:
            {
                "Architecture1": "Report content for Architecture1",
                "Architecture2": "Report content for Architecture2"
            }

    def report_compiler_node(state: OverallState):
        Compiles reports into a dictionary with anonymized names and updates the system state.

        Args:
            state (OverallState): The current system state containing:
                - "reports" (list): List of architecture names to load reports from.

        Returns:
            OverallState: Updated system state with compiled reports, where each report includes:
                - "real_name" (str): The original architecture name.
                - "anonymized_name" (str): Anonymized name for the report.
                - "report" (str): The report content.

        Example:
            state = {
                "reports": ["Architecture1", "Architecture2"]
            }
            updated_state = report_compiler_node(state)
            print(updated_state["reports"])

        Output:
            {
                "Architecture1": {
                    "real_name": "Architecture1",
                    "anonymized_name": "Report_1",
                    "report": "Report content for Architecture1"
                },
                "Architecture2": {
                    "real_name": "Architecture2",
                    "anonymized_name": "Report_2",
                    "report": "Report content for Architecture2"
                }
            }
"""

import os
from typing import List

from graphEvaluator.states import OverallState


# Function to load reports into a dictionary
def load_reports(architectures: List[str]) -> dict[str, str]:
    """
    Loads reports into a dictionary from the specified architectures.

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
        report_path = os.path.join(f"../graph{arch}", "output.md")
        if os.path.exists(report_path):
            print("The", f"graph{arch}", "report downloaded!")
            with open(report_path, "r") as file:
                reports[arch] = file.read()
        else:
            print(f"Warning: Report for {arch} not found at {report_path}")
    return reports


def report_compiler_node(state: OverallState):
    """
    Compiles reports into a dictionary with anonymized names and updates the system state.

    Args:
        state (OverallState): The current system state containing:
            - "reports" (list): List of architecture names to load reports from.

    Returns:
        OverallState: Updated system state with compiled reports, where each report includes:
            - "real_name" (str): The original architecture name.
            - "anonymized_name" (str): Anonymized name for the report.
            - "report" (str): The report content.

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