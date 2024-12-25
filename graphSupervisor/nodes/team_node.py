import os
from pyexpat.errors import messages

from httpx import Headers
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.constants import END

from graphSupervisor.states import ResearchState

llm = ChatOpenAI(model_name=os.getenv("MODEL"))

analyst_prompt = """
# Role & Context
You are: {person}
You are in {team} with {reviewer}, who will provide a review and share their opinion with you.
You are tasked with performing a **needs analysis** for your customer on the topic: {topic}

# Data Source
Here are the **questionnaire results**: {questionnaire}

# Objective
Your primary goal is to **analyze the current state of the customer** based on the questionnaire results and, once received, **integrate the reviewer's feedback** into your analysis.

# Guidelines
- Generate **only an analysis** based on the questionnaire results.
- Focus **solely on your persona, competencies, and tasks**.

# Constraints
- **Do not analyze aspects outside of your persona or competencies.**
- **Do not recommend any solutions yet.**

# Final Note
Keep your analysis focused, clear, and aligned with the given responsibilities and data.
Behave like a provided persona.
Start your messages from your name!
"""


reviewer_prompt = """
# Role & Context
You are: {person}
You are in {team} with {analyst}, who will make an analysis and share it with you.
You are tasked with assisting your analyst on the topic: {topic}

# Data Source
Here are the questionnaire results: {questionnaire}

# Objective
Your primary task is to create a constructive and insightful review based on the provided analysis and questionnaire results.

# Guidelines
1. **Constructive:** Provide actionable and helpful recommendations.
2. **Specific:** Avoid generalities; include clear examples directly tied to the analysis.
3. **Manageable:** Ensure your recommendations are practical and achievable for the customer.

# Constraints
- Base your recommendations **solely on the provided analysis**.
- Stay **aligned with your role, expertise, and responsibilities**.
- Avoid commenting on aspects outside your defined scope.

# Final Note
Focus on delivering a review that adds value, clarity, and direction to the analysis provided.
Behave like a provided persona.
Start your messages from your name!
"""



def analyst_node(state):
    topic = state["team_topic"]

    team_name = state["name"]
    team_description = state["description"]

    reviewer_info = state["reviewer"]
    analyst_info = state["analyst"]

    questionnaire = state["team_questionnaire"]

    print(f"Analyst node {team_name} activated.")

    system_prompt = analyst_prompt.format(topic=topic,
                                          team = team_name + "\n" + team_description,
                                          reviewer = reviewer_info,
                                          person = analyst_info,
                                          questionnaire = questionnaire)

    messages = state["messages"]

    if len(messages) != 0:
        last_message = "Your previous report: \n" + messages[-2].content +"\n\n\nReviewers recommendations: \n" + messages[-1].content
    else:
        last_message = "This is the beginning of conversation. Make your initial analysis based on the questionnaire results."

    print("========================================")
    print(last_message)
    print("========================================")

    llm_messages = [SystemMessage(content=system_prompt),
                last_message
                ]

    return {"messages": [llm.invoke(llm_messages).content]}
    # return {"messages": [AIMessage("Analyst answer " + state["analyst_prompt"][0:25])]  + state.get("messages", [])} # For test


def reviewer_node(state):
    topic = state["team_topic"]

    team_name = state["name"]
    team_description = state["description"]

    reviewer_info = state["reviewer"]
    analyst_info = state["analyst"]

    questionnaire = state["team_questionnaire"]

    print(f"Reviewer node {team_name} activated.")

    system_prompt = reviewer_prompt.format(topic=topic,
                                          team = team_name + "\n" + team_description,
                                          analyst = analyst_info,
                                          person = reviewer_info,
                                          questionnaire = questionnaire)



    last_message = state["messages"][-1].content
    print("++++++++++++++++++++++++++++++++++++++++")
    print(last_message)
    print("++++++++++++++++++++++++++++++++++++++++")

    messages = [SystemMessage(content=system_prompt),
                last_message,
                ]


    return {"messages": [llm.invoke(messages).content]}
    # return {"messages": [AIMessage("Reviewers answer " + state["reviewer_prompt"][0:25])] + state.get("messages", [])} # For test


def should_continue(state: ResearchState):
    messages = state.get("messages", [])
    # Check if the number of messages is 6 or more
    if len(messages) >= 7:

        # Return the END constant and the overall state update
        state["reviews"].append(messages[-1].content)
        return END

    # If the condition is not met, return the next node
    return "Reviewer"

