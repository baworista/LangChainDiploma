"""
Module: prompt_generation.

This module provides functions to generate structured prompts for agents, users, and summary agents
within a network workflow. These prompts are dynamically created based on agent roles, responsibilities,
and the current state of the workflow.

Modules and Constants Used:
    - AGENT_PROMPT_TEMPLATE: Template for agent-specific prompts.
    - AGENTS_DEFINITIONS: Dictionary defining roles and responsibilities for each agent.
    - SUMMARY_AGENT_PROMPT_TEMPLATE: Template for generating summary agent prompts.
    - USER_PROMPT_TEMPLATE: Template for generating user prompts.

Functions:
    - generate_agent_prompt: Generates a prompt for a specific agent based on its definition.
    - create_user_prompt: Generates a prompt for the user based on the current workflow state.
    - create_summary_agent_prompt: Generates a prompt for the summary agent to consolidate analyses and reports.
"""

from graphNetwork.prompts.prompt_templates import AGENT_PROMPT_TEMPLATE
from graphNetwork.prompts.agent_definition import AGENTS_DEFINITIONS
from graphNetwork.prompts.summary_agent_prompt import SUMMARY_AGENT_PROMPT_TEMPLATE
from graphNetwork.prompts.user_prompt import USER_PROMPT_TEMPLATE


def generate_agent_prompt(agent_name):
    """
    Generate a prompt for a specific agent based on its role and responsibilities.

    Args:
        agent_name (str): The name of the agent (e.g., "HR_Agent", "IT_Agent").

    Returns:
        str: A formatted prompt string tailored to the agent's role and mission.

    Raises:
        ValueError: If the specified agent name is not defined in `AGENTS_DEFINITIONS`.

    Example:
        agent_name = "HR_Agent"
        prompt = generate_agent_prompt(agent_name)
        print(prompt)
    """
    agent_data = AGENTS_DEFINITIONS.get(agent_name)
    if not agent_data:
        raise ValueError(f"Agent '{agent_name}' is not defined in AGENTS_DEFINITIONS.")
    return AGENT_PROMPT_TEMPLATE.format(**agent_data)


def create_user_prompt(state):
    """
    Generate a user prompt based on the current workflow state.

    Args:
        state (dict): The current state of the workflow, containing:
            main_task (str): The primary task being addressed.
            task (str): The current subtask.
            questionnaire (str): The questionnaire data provided by the user.
            good_practices (str): Best practices relevant to the workflow.
            analysis (str): The analysis results from agents.
            questions (str or list, optional): Questions asked during the workflow. Defaults to "NO QUESTIONS".
            processed_agents (list, optional): Agents that have already been processed. Defaults to an empty list.

    Returns:
        str: A formatted prompt string for the user.

    Example:
        state = {
            "main_task": "Improve team collaboration",
            "task": "Analyze team dynamics",
            "questionnaire": "Survey results...",
            "good_practices": "Industry best practices...",
            "analysis": "Initial analysis...",
            "questions": ["What are the main blockers?"],
            "processed_agents": ["HR_Agent", "IT_Agent"],
            }
        prompt = create_user_prompt(state)
        print(prompt)
    """
    questions = state.get("questions", "NO QUESTIONS")
    processed_agents = state.get("processed_agents", [])
    task = state.get("task", "NO SUBTASK YET")
    analysis = state.get("analysis", "NO ANALYSIS YET")

    return USER_PROMPT_TEMPLATE.format(main_task=state["main_task"], task=task, questionnaire=state["questionnaire"], good_practices=state["good_practices"], analysis=analysis, questions=questions, processed_agents=", ".join(processed_agents))

def create_summary_agent_prompt(state):
    """
    Generate a prompt for the summary agent to consolidate analyses and generate a final report.

    Args:
        state (dict): The current state of the workflow, containing:
            main_task (str): The primary task being addressed.
            analysis (str): Consolidated analysis results.
            questionnaire (str): The questionnaire data provided by the user.
            good_practices (str): Best practices relevant to the workflow.
            processed_agents (list, optional): Agents that have already been processed. Defaults to an empty list.

    Returns:
        str: A formatted prompt string for the summary agent.

    Example:
        state = {
            "main_task": "Enhance knowledge sharing",
            "analysis": "Combined agent analyses...",
            "questionnaire": "Questionnaire data...",
            "good_practices": "Recommended tools and practices...",
            "processed_agents": ["KM_Agent", "BP_Agent"],
             }
        prompt = create_summary_agent_prompt(state)
        print(prompt)
    """
    return SUMMARY_AGENT_PROMPT_TEMPLATE.format(main_task=state["main_task"], analysis=state["analysis"], questionnaire=state["questionnaire"], good_practices=state["good_practices"], processed_agents=", ".join(state["processed_agents"]) if state["processed_agents"] else "None")
