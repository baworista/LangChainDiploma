import os
from dotenv import load_dotenv
from graphEvaluator.nodes.states import OverallState

# Install bert-score library
# pip install bert-score
from bert_score import score

load_dotenv()

def bert_evaluator_node(state: OverallState):
    print("BERT Evaluator activated.")

    reports = state["reports"]
    reference_text = state.get("reference_text", "")  # Reference text for comparison

    if not reference_text:
        raise ValueError("Reference text is required for BERT evaluation.")

    results = []

    # Evaluate each report using BERTScore
    for anonymized_name, report_content in reports.items():
        print(f"Evaluating report: {anonymized_name}")

        # Compute BERTScore
        P, R, F1 = score([report_content], [reference_text], lang="en", verbose=True)

        results.append({
            "anonymized_name": anonymized_name,
            "scores": [
                {
                    "criterion_name": "Precision",
                    "score": P.mean().item(),
                    "comment": "Precision measures the fraction of words in the report that have corresponding words in the reference text."
                },
                {
                    "criterion_name": "Recall",
                    "score": R.mean().item(),
                    "comment": "Recall measures the fraction of words in the reference text that have corresponding words in the report."
                },
                {
                    "criterion_name": "F1 Score",
                    "score": F1.mean().item(),
                    "comment": "F1 Score is the harmonic mean of Precision and Recall, representing the overall semantic overlap."
                }
            ],
            "overall_comment": "The BERT evaluation provides insights into the semantic overlap between the report and the reference text. High scores indicate strong alignment with the reference."
        })

    # Construct the final output
    detailed_result = {"evaluator_reports": results}

    return detailed_result
