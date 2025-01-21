from dotenv import load_dotenv
from graphEvaluator.states import OverallState

# Install DeepEval library
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval

load_dotenv()

def g_eval_evaluator_node(state: OverallState):
    print("G-Eval Evaluator activated.")

    reports = state["reports"]
    criteria = [
        {
            "name": "Relevance",
            "criteria": "Relevance - How well does the report address the task?"
        },
        {
            "name": "Factuality",
            "criteria": "Factuality - Does the report contain any factual errors?"
        },
        {
            "name": "Completeness",
            "criteria": "Completeness - Does the report fully cover all aspects of the task (diagnosis and recommendations)?"
        },
        {
            "name": "Clarity",
            "criteria": "Clarity - Is the report well-structured and easy to understand?"
        },
        {
            "name": "Actionability",
            "criteria": "Actionability - Are the recommendations practical and applicable?"
        }
    ]

    results = []

    anonymized_reports = {
        report_data["anonymized_name"]: report_data["report"]
        for real_name, report_data in reports.items()
    }

    # Evaluate each report using G-Eval
    for anonymized_name, report_content in anonymized_reports.items():
        print(f"Evaluating report: {anonymized_name}")

        report_results = []

        for criterion in criteria:
            test_case = LLMTestCase(
                input="Evaluation based on criterion: " + criterion["criteria"],
                actual_output=report_content
            )

            metric = GEval(
                name=criterion["name"],
                criteria=criterion["criteria"],
                evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT]
            )

            metric.measure(test_case)

            report_results.append({
                "criterion_name": criterion["name"],
                "score": metric.score,
                "comment": metric.reason
            })

        results.append({
            "anonymized_name": anonymized_name,
            "scores": report_results
        })

    # Construct the final output
    detailed_result = {"g-evaluator": results}

    return {"evaluator_reports": [detailed_result]}
