import os
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model_name=os.getenv("MODEL_SUPERVISOR"))


# Function to load reports into a dictionary
def load_reports(architectures):
    reports = {}
    for arch in architectures:
        report_path = os.path.join(f"graph{arch}", "output.md")
        if os.path.exists(report_path):
            print("The", f"graph{arch}", "report downloaded!")
            with open(report_path, "r") as file:
                reports[arch] = file.read()
        else:
            print(f"Warning: Report for {arch} not found at {report_path}")
    return reports



# Evaluator function
def evaluate_with_gpt4(reports):
    anonymized_reports = {f"Report_{i + 1}": content for i, (arch, content) in enumerate(reports.items())}

    evaluation_results = {}

    for name, report in anonymized_reports.items():
        prompt = f"""
        Task: Evaluate the provided report.

        Report: {report}

        Evaluate the report based on the following criteria:
        1. Relevance: How well does the report address the task?
        2. Factuality: Does the report contain any factual errors?
        3. Completeness: Does the report fully cover all aspects of the task (diagnosis and recommendations)?
        4. Clarity: Is the report well-structured and easy to understand?
        5. Actionability: Are the recommendations practical and applicable?

        Provide a score (1-5) for each criterion and include a brief explanation.
        """
        response = llm.invoke([SystemMessage(content=prompt)])
        evaluation_results[name] = response.content

    return evaluation_results


# Find the best report
def find_best_report(evaluation_results):
    scores = {}

    for name, evaluation in evaluation_results.items():
        try:
            # Extract scores assuming the evaluator returns them in a structured way
            lines = evaluation.split("\n")
            score_lines = [line for line in lines if line.startswith("Score")]
            total_score = sum(int(line.split(":")[1].strip()) for line in score_lines)
            scores[name] = total_score
        except Exception as e:
            print(f"Error parsing evaluation for {name}: {e}")

    best_report = max(scores, key=scores.get)
    return best_report, scores[best_report]


# Main workflow
if __name__ == "__main__":
    architectures = ["Supervisor", "Network", "HierarchicalTeams"]

    reports = load_reports(architectures)

    if not reports:
        print("No reports loaded. Exiting.")
    else:
        evaluation_results = evaluate_with_gpt4(reports)
        best_report, best_score = find_best_report(evaluation_results)

        print(f"The best report is {best_report} with a score of {best_score}")
        print(f"Evaluation results:\n{evaluation_results}")
