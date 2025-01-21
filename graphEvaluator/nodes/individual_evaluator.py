import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from graphEvaluator.states import OverallState
from graphEvaluator.schema import EvaluatorOutput

load_dotenv()
llm = ChatOpenAI(model_name=os.getenv("MODEL_SUPERVISOR"))

evaluator_prompt = """
    Task: You are an individual evaluator reviewing a single report compiled by an anonymous team on topic: {topic}.
    You are aware that there are multiple reports, but you will evaluate only this one in isolation.
    With asked questions and answers on it: {questionnaire}

    Report: {report}

    Evaluate the report based on the following criteria:
    1. Relevance: How well does the report address the task?
    2. Factuality: Does the report contain any factual errors?
    3. Completeness: Does the report fully cover all aspects of the task (diagnosis and recommendations)?
    4. Clarity: Is the report well-structured and easy to understand?
    5. Actionability: Are the recommendations practical and applicable?

    **Provide a score (1-5) for each criterion and include a detailed and specific explanation for the report.**
    **Ensure that your evaluation is critical and fair: Avoid giving the highest scores (5) unless the report clearly demonstrates exceptional quality in that criterion.**
    **Justify your evaluation and highlight key strengths and weaknesses of the report.**
"""


def evaluate_single_report(report: str, topic: str, questionnaire: str) -> EvaluatorOutput:
    """
    Evaluate a single report using LLM and return the structured output.
    """
    system_prompt = evaluator_prompt.format(
        topic=topic,
        questionnaire=questionnaire,
        report=report
    )

    structured_llm = llm.with_structured_output(EvaluatorOutput)
    system_message = SystemMessage(content=system_prompt)

    # Query the LLM and get the structured output
    return structured_llm.invoke([system_message])


def individual_evaluator_node(state: OverallState):
    print("Individual Evaluator activated.")

    reports = state["reports"]
    topic = state["topic"]
    questionnaire = state["questionnaire"]

    results = []

    anonymized_reports = {
        report_data["anonymized_name"]: report_data["report"]
        for real_name, report_data in reports.items()
    }

    # Evaluate each report using G-Eval
    for anonymized_name, report_content in anonymized_reports.items():
        print(f"Evaluating report: {anonymized_name}")

        # Evaluate the report in isolation
        evaluation_result = evaluate_single_report(
            report=report_content,
            topic=topic,
            questionnaire=questionnaire
        )

        # Append the structured evaluation to results
        results.append({
            "anonymized_name": anonymized_name,
            "scores": evaluation_result.scores,
            "overall_comment": evaluation_result.overall_comment
        })

    # Construct the final output
    detailed_result = {"individual_evaluator": results}

    return {"evaluator_reports": [detailed_result]}