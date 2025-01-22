"""
Module for the final evaluation node in a multi-agent system.

This module defines the `final_evaluator_node` function, which uses a language model to select
the best report from a set of submissions. The evaluation is based on a comprehensive analysis
of the reports, questionnaire, and feedback from other evaluators.

Functionality:
    - Accepts the overall state, including the topic, questionnaire, reports, and evaluator feedback.
    - Uses a predefined prompt to guide the language model in selecting the best report.
    - Returns the selected report and justification for its selection.

Evaluation Workflow:
1. Analyze the provided materials:
   - Main topic.
   - Questionnaire used for assessment.
   - Reports submitted by agents.
   - Evaluator feedback on each report.
2. Select the best report based on the evaluation criteria.
3. Justify the selection with a detailed explanation.

Dependencies:
    - langchain_core.messages: For creating system messages for the language model.
    - langchain_openai: For interacting with OpenAI's language model.
    - graphEvaluator.states: Contains the `OverallState` definition for the workflow state.

Function:
    - final_evaluator_node: The core function for selecting the best report and providing a justification.

Prompt Structure:
    - Main Topic: The central theme of the evaluation.
    - Questionnaire: Questions used to guide the reports' creation.
    - Reports: Submissions prepared by agents addressing the main topic.
    - Evaluator Reports: Feedback from other evaluators on the reports.
    - Objective: Instructions for selecting the best report and justifying the choice.

Example Usage:
    state = {
        "topic": "Optimize team collaboration in multinational organizations.",
        "questionnaire": "Survey data about team dynamics and communication barriers.",
        "reports": {
            "Report_1": "Detailed analysis of team performance.",
            "Report_2": "Recommendations for improving collaboration."
        },
        "evaluator_reports": [
            {"Report_1": {"relevance": 4, "clarity": 5, "actionability": 3}},
            {"Report_2": {"relevance": 5, "clarity": 4, "actionability": 4}}
        ]
    }

    output = final_evaluator_node(state)
    print(output["the_best_report_info"])

Output:
    {
        "the_best_report_info": "Report_2 excels in addressing the topic, providing actionable recommendations, and being clear and concise."
    }
"""

import os

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from graphEvaluator.states import OverallState


llm = ChatOpenAI(model_name=os.getenv("MODEL_SUPERVISOR"))

eval_prompt="""
You are the final evaluator in a multi-agent system tasked with selecting the best report. Your role is to carefully analyze and compare all the provided materials, including:

Main Topic: The central theme or subject matter of the evaluation.
{topic}
Questionnaire: A set of questions used to assess the reports.
{questionnaire}
Reports: The submissions prepared by agents addressing the main topic and questionnaire.
{reports}
Evaluator Reports: Feedback or assessments from other evaluators regarding the reports.
{evaluator_reports}

Your Objective: Based on provided information, select the best report. Provide a justification for your decision, clearly explaining why the chosen report excels in meeting the evaluation criteria.
"""


def final_evaluator_node(state: OverallState):
    """
    Selects the best report from the provided submissions and justifies the selection.

    Args:
        state (OverallState): The current overall state of the workflow, containing:
            - "topic" (str): The main topic of the evaluation.
            - "questionnaire" (str): The questionnaire used to assess the reports.
            - "reports" (dict): A dictionary of reports submitted by agents.
            - "evaluator_reports" (list): Feedback or assessments from other evaluators.

    Returns:
        dict: A dictionary containing the selected report and justification under the key `the_best_report_info`.

    Example:
        state = {
            "topic": "Optimize team collaboration in multinational organizations.",
            "questionnaire": "Survey data about team dynamics and communication barriers.",
            "reports": {"Report_1": "Detailed analysis of team performance.", "Report_2": "Recommendations for improving collaboration."},
            "evaluator_reports": [{"Report_1": {"relevance": 4, "clarity": 5, "actionability": 3}}, {"Report_2": {"relevance": 5, "clarity": 4, "actionability": 4}}],
        }

        output = final_evaluator_node(state)
        print(output["the_best_report_info"])
    """
    print("Final Evaluator activated.")

    topic = state["topic"]
    questionnaire = state["questionnaire"]
    reports = state["reports"]
    evaluator_reports = state["evaluator_reports"]

    prompt = eval_prompt.format(topic=topic,
                                questionnaire=questionnaire,
                                reports=reports,
                                evaluator_reports=evaluator_reports)

    prompt = [SystemMessage(content=prompt)]


    output = llm.invoke(prompt)

    return {"the_best_report_info": output}