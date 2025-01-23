"""
Module for managing agent-based workflows in a network.

This module initializes agents to handle various tasks using a structured language model.
Agents communicate using prompts and states, progressing through the workflow until completion.

Key Features:
- Initialize agents with specific roles (e.g., Consulting, HR, BP, KM, IT).
- Use prompts to guide agent tasks and generate responses.
- Process responses to determine the next agent and update the workflow state.

Modules Used:
    - os: For environment variable management.
    - dotenv: For loading environment variables from a `.env` file.
    - langchain_openai: For interacting with OpenAI's language model.
    - langgraph.types: For managing commands and transitions between agents.
    - graphNetwork.states: Custom states for managing the workflow.
    - graphNetwork.schemas: Custom schema definitions for structured outputs.
    - graphNetwork.prompts.generators: Utilities for generating user and agent prompts.

Functions:
    - agent_handler: Handles the execution of a generic agent, including prompt generation and response processing.
    - Consulting_Agent: Executes the Consulting Agent's workflow.
    - HR_Agent: Executes the HR Agent's workflow.
    - BP_Agent: Executes the BP Agent's workflow.
    - KM_Agent: Executes the KM Agent's workflow.
    - IT_Agent: Executes the IT Agent's workflow.
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from graphNetwork.states import OverallState
from graphNetwork.schemas import Output
from graphNetwork.prompts.generators import create_user_prompt, generate_agent_prompt

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(model=os.getenv("MODEL_SUPERVISOR"))
model = llm.with_structured_output(Output)

def agent_handler(state: OverallState, agent_prompt: str):
    """
    Handle the execution of a generic agent.

    This function creates a structured prompt for the agent, invokes the language model,
    and processes the response to determine the next agent or update the workflow state.

    Args:
        state (OverallState): The current state of the workflow.
        agent_prompt (str): The prompt specific to the agent's role and tasks.

    Returns:
        dict or Command: A dictionary with the updated state if the workflow ends, or a `Command` object with
            instructions for the next agent.

    Raises:
        ValueError: If the language model response is invalid or incomplete.

    Examples:
        updated_state = agent_handler(state, "Agent Prompt Example")
    """
    user_prompt = create_user_prompt(state)

    messages = [
        {"role": "system", "content": agent_prompt},
        {"role": "user", "content": user_prompt}
    ]
    ai_msg = model.invoke(messages)

    print("""
RESPONSE\n" 
{ai_msg.analysis}
==========================\n
NEXT AGENT: {ai_msg.next_agent}
TASK: {ai_msg.task}
QUESTIONS: {ai_msg.questions}
==========================\n
    """.format(ai_msg=ai_msg))

    if ai_msg.next_agent != "__end__":
        return Command(
            goto=ai_msg.next_agent,
            update={
                "analysis": [ai_msg.analysis],
                "task": ai_msg.task,
                "questions": ai_msg.questions,
                "processed_agents": [ai_msg.name, ai_msg.next_agent],
            }
        )

    return {"analysis": [ai_msg.analysis]}

def Consulting_Agent(state: OverallState):
    """
    Execute the Consulting Agent's workflow.

    Args:
        state (OverallState): The current state of the workflow.

    Returns:
        dict or Command: Updated state or transition command.

    Examples:
        result = Consulting_Agent(current_state)
    """
    return agent_handler(state, generate_agent_prompt("Consulting_Agent"))

def HR_Agent(state: OverallState):
    """
    Execute the HR Agent's workflow.

    Args:
        state (OverallState): The current state of the workflow.

    Returns:
        dict or Command: Updated state or transition command.

    Examples:
        result = HR_Agent(current_state)
    """
    return agent_handler(state, generate_agent_prompt("HR_Agent"))

def BP_Agent(state: OverallState):
    """
    Execute the BP Agent's workflow.

    Args:
        state (OverallState): The current state of the workflow.

    Returns:
        dict or Command: Updated state or transition command.

    Examples:
        result = BP_Agent(current_state)
    """
    return agent_handler(state, generate_agent_prompt("BP_Agent"))

def KM_Agent(state: OverallState):
    """
    Execute the KM Agent's workflow.

    Args:
        state (OverallState): The current state of the workflow.

    Returns:
        dict or Command: Updated state or transition command.

    Examples:
        result = KM_Agent(current_state)
    """
    return agent_handler(state, generate_agent_prompt("KM_Agent"))

def IT_Agent(state: OverallState):
    """
    Execute the IT Agent's workflow.

    Args:
        state (OverallState): The current state of the workflow.

    Returns:
        dict or Command: Updated state or transition command.

    Examples:
        result = IT_Agent(current_state)
    """
    return agent_handler(state, generate_agent_prompt("IT_Agent"))