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