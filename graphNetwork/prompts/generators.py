from graphNetwork.prompts.prompt_templates import AGENT_PROMPT_TEMPLATE
from graphNetwork.prompts.agent_definition import AGENTS_DEFINITIONS
from graphNetwork.prompts.summary_agent_prompt import SUMMARY_AGENT_PROMPT_TEMPLATE
from graphNetwork.prompts.user_prompt import USER_PROMPT_TEMPLATE


def generate_agent_prompt(agent_name):
    agent_data = AGENTS_DEFINITIONS.get(agent_name)
    if not agent_data:
        raise ValueError(f"Agent '{agent_name}' is not defined in AGENTS_DEFINITIONS.")
    return AGENT_PROMPT_TEMPLATE.format(**agent_data)


def create_user_prompt(state):
    questions = state.get("questions", "NO QUESTIONS")
    processed_agents = state.get("processed_agents", [])
    task = state.get("task", "NO SUBTASK YET")
    analysis = state.get("analysis", "NO ANALYSIS YET")

    return USER_PROMPT_TEMPLATE.format(main_task=state["main_task"], task=task, questionare=state["questionare"], good_practices=state["good_practices"], analysis=analysis, questions=questions, processed_agents=", ".join(processed_agents))

def create_summary_agent_prompt(state):
    return SUMMARY_AGENT_PROMPT_TEMPLATE.format(main_task=state["main_task"], analysis=state["analysis"], questionare=state["questionare"], good_practices=state["good_practices"], processed_agents=", ".join(state["processed_agents"]) if state["processed_agents"] else "None")
