import os
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model_name=os.getenv("MODEL_SUPERVISOR"))


# Функция для оценки через GPT-4
def evaluate_with_gpt4(state):
    prompt = """
    Task: {task}
    questionnaire: {questionnaire}
    Best Practices: {good_practices}
    Report: {report}

    Evaluate the report based on the following criteria:
    1. Relevance: How well does the report address the task?
    2. Factuality: Does the report contain any factual errors?
    3. Completeness: Does the report fully cover all aspects of the task (diagnosis and recommendations)?
    4. Clarity: Is the report well-structured and easy to understand?
    5. Actionability: Are the recommendations practical and applicable?

    Provide a score (1-5) for each criterion and include a brief explanation.
    """.format(task=state["main_task"], questionnaire=state["questionnaire"], good_practices=state["good_practices"], report=state["final_report"])
    response = llm.invoke([SystemMessage(content=prompt)])
    print(response)
    return response
