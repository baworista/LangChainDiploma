import os

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticToolsParser
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from schemas import Analyst
from testfiles.bla1 import prompt

load_dotenv()



@tool
def create_analysts_tool(topic: str) -> dict:
    """
    Tool to create AI analysts based on a provided topic.
    Accepts the topic as a string and returns the generated analysts in a JSON-serializable format.
    """
supervisor_instruction = """
You are tasked with creating a set of AI analyst personas. Follow these instructions carefully:

First, review the provided research topic.

Next, create four AI analysts:
1. Human Resources Analyst, focusing on team dynamics and performance, team collaboration, and human trainings and development in the context of the topic.
2. Business Process Analyst, focusing on business process optimization, business process automation, and business process management in the context of the topic.
3. Knowledge Management Analyst, focusing on knowledge management processes, knowledge sharing, and knowledge tools in the context of the topic.
4. IT Systems Analyst, specializing in IT systems, IT tools, and IT strategies in the context of the topic.
"""

    pydantic_parser = PydanticToolsParser(tools=[Analyst])
    structured_llm =

    human_message = HumanMessage(content=f"Generate the set of analysts. Here is the topic: {topic}.")

    # Генерация аналитиков
    perspectives: Perspectives = structured_llm.invoke([system_message, human_message])

    # Преобразуем в сериализуемый формат
    serialized_analysts = [
        {
            "name": analyst.name,
            "role": analyst.role,
            "description": analyst.description,
        }
        for analyst in perspectives.analysts
    ]

    return {"analysts": serialized_analysts}


llm = ChatOpenAI(temperature=0, model_name=os.getenv('MODEL'))

supervisor_chain = prompt | llm.bind_tools([create_analysts_tool])
