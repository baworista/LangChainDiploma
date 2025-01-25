"""
Module for evaluating team-generated reports using a comprehensive evaluator node.

This module defines the `comprehensive_evaluator_node` function, which evaluates reports submitted by
different teams based on predefined criteria using a language model. The evaluation process is anonymized
to ensure fairness and objectivity, and each report is scored on five key criteria.

Functionality:
    - Accepts the current workflow state, including the topic, questionnaire, and reports.
    - Anonymizes report data to prevent bias in evaluations.
    - Scores reports based on relevance, factuality, completeness, clarity, and actionability.
    - Returns structured evaluation results in a standardized format for further processing.

Evaluation Criteria:
    1. **Relevance**: How well the report addresses the task.
    2. **Factuality**: Whether the report contains any factual errors.
    3. **Completeness**: Coverage of all aspects of the task, including diagnosis and recommendations.
    4. **Clarity**: Whether the report is well-structured and easy to understand.
    5. **Actionability**: Practicality and applicability of the recommendations.

Dependencies:
    - `langchain_core.messages`: For generating system prompts for the language model.
    - `langchain_openai`: For querying OpenAI's language model.
    - `graphEvaluator.states`: Defines the `OverallState` workflow structure.
    - `graphEvaluator.schema`: Provides the `StructuredEvaluatorOutput` for standardized evaluations.

Functions:
    - comprehensive_evaluator_node: Evaluates reports using a language model and returns structured results.
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from graphEvaluator.states import OverallState
from graphEvaluator.schema import StructuredEvaluatorOutput

load_dotenv()
llm = ChatOpenAI(model_name=os.getenv("MODEL_SUPERVISOR"))

evaluator_prompt = """
    Task: You are a comprehensive evaluator reviewing the reports compiled by the different teams on topic: {topic}.
    With asked questions and answers on it: {questionnaire}
    The names are anonymized to you be objective in your evaluation.
    You have access to the following reports:

    Reports: {reports}

    Evaluate each report based on the following criteria:
    1. Relevance: How well does the report address the task?
    2. Factuality: Does the report contain any factual errors?
    3. Completeness: Does the report fully cover all aspects of the task (diagnosis and recommendations)?
    4. Clarity: Is the report well-structured and easy to understand?
    5. Actionability: Are the recommendations practical and applicable?
    
    **Provide a score (1-5) for each criterion and include a detailed and specific explanation for each report.**
    **Ensure that your evaluation is critical and fair: Avoid giving the highest scores (5) unless the report clearly demonstrates exceptional quality in that criterion.**
    **Justify your choice by explicitly comparing it with the others.**
    **Note: You are only one of several evaluators. Make your evaluation based on a balanced and unbiased analysis, avoiding assumptions or over-optimistic scoring.**
"""

def comprehensive_evaluator_node(state: OverallState):
    """
    Evaluate team-generated reports using a comprehensive language model.

    This function processes reports provided in the workflow state, anonymizes their data, and evaluates
    them based on predefined criteria. The results include structured feedback and scores for each report.

    Args:
        state (OverallState): The current workflow state, which includes:
            - topic (str): The topic being evaluated.
            - questionnaire (str): Questions and answers used for evaluation.
            - reports (dict): A dictionary of anonymized reports submitted by teams.

    Returns:
        dict: A structured evaluation report, containing scores and feedback for each report.

    Example:
        state = {
            "topic": "Optimize organizational IT systems.",
            "questionnaire": "Survey responses about IT satisfaction.",
            "reports": {
                "Report_1": "Details about IT infrastructure.",
                "Report_2": "Details about team collaboration."
            }
        }

        output = comprehensive_evaluator_node(state)
        print(output["evaluator_reports"])
    """
    print("Comprehensive Evaluator activated.")

    reports = state["reports"]

    # Step 1: Create anonymized mapping
    anonymized_reports = {anonymized_name: report for i, (anonymized_name, report) in enumerate(reports.items())}

    structured_llm = llm.with_structured_output(StructuredEvaluatorOutput)

    system_prompt = evaluator_prompt.format(
        topic=state["topic"],
        questionnaire=state["questionnaire"],
        reports=anonymized_reports
    )

    # Step 2: LLM Query
    system_message = SystemMessage(content=system_prompt)
    output = structured_llm.invoke([system_message])

    # Step 5: Construct the result
    detailed_result = {"comprehensive_evaluator": output.reports}

    return {"evaluator_reports": [detailed_result]}









# def comprehensive_evaluator_node(state: OverallState):
#     print("Comprehensive Evaluator activated.")
#
#     reports = state["reports"]
#
#     # Step 1: Create anonymized mapping
#     anonymized_reports = {f"Report_{i + 1}": content for i, (arch, content) in enumerate(reports.items())}
#     reverse_mapping = {f"Report_{i + 1}": arch for i, arch in enumerate(reports.keys())}
#
#     structured_llm = llm.with_structured_output(EvaluatorOutput)
#
#
#     system_prompt = evaluator_prompt.format(
#         topic=state["topic"],
#         questionnaire=state["questionnaire"],
#         reports=anonymized_reports
#     )
#
#     # Step 2: LLM Query
#     system_message = SystemMessage(content=system_prompt)
#     output = structured_llm.invoke([system_message])
#
#     # Step 3: Extract relevant fields from the output
#     anonymized_name = output.anonymized_name  # Extract the anonymized name
#     description = output.description  # Extract the description
#
#     # Step 4: Map back the anonymized name to the original name
#     original_name = reverse_mapping.get(anonymized_name, anonymized_name)
#
#     # Step 5: Construct the result
#     detailed_result = {original_name: description}
#
#     return {"evaluator_reports": [detailed_result]}
