import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from graphEvaluator.nodes.states import OverallState
from graphEvaluator.schema import EvaluatorOutput, StructuredEvaluatorOutput

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
    detailed_result = {"comprehensive_evaluator": output}

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
