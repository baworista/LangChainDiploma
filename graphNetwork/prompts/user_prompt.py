"""
Template for generating user prompts in a multi-agent system workflow.

The `USER_PROMPT_TEMPLATE` is designed to guide the user through a structured workflow
by providing relevant information, tasks, analysis, and questions for the next agent.
It ensures that agents collaborate effectively, ask the right questions, and adhere to
the established process.

Purpose:
    - Defines the main goal of the task.
    - Presents the subtask the user should focus on.
    - Provides relevant context including questionnaires and best practices.
    - Summarizes the existing analysis and highlights unanswered questions.

Template Variables:
    - main_task (str): The primary goal of the task.
    - task (str): A specific subtask the user should focus on.
    - questionnaire (str): The questionnaire data provided by the user or agents.
    - good_practices (str): Best practices to be considered during the task.
    - analysis (str): The current analysis, summarizing insights from previous agents.
    - questions (str or list): Any specific questions that need to be asked to agents.
    - processed_agents (str): A list of agents who have already contributed to the task.

Sections of the Prompt:
1. **Main Goal**: Clarifies the overall objective of the task.
2. **Subtask**: Specifies the user’s current focus or subtask.
3. **Questionnaire**: Displays the questionnaire data to guide the analysis.
4. **Best Practices**: Provides industry or task-specific best practices.
5. **Additional Context**: Instructs the user to retain previous analysis and add new insights.
6. **Current Analysis**: A summary of the analysis from previous agents.
7. **Questions for the Agent**: Lists questions the user wants to ask the next agent.
8. **Important Instructions**: Informs the user about the agents who have already contributed and helps determine the next agent to ask.

Rules:
- Ensure clarity and conciseness.
- Do not ask previously asked agents; focus on new ones or return to the summary agent if all agents have been asked.
- Respond in a structured format and specify the next agent or indicate the task is complete.

Usage Example:
    state = {
        "main_task": "Improve team collaboration",
        "task": "Analyze team communication barriers",
        "questionnaire": "Survey data about team interactions",
        "good_practices": "Effective communication practices",
        "analysis": "Previous analysis from HR and IT agents.",
        "questions": "What specific barriers prevent collaboration?",
        "processed_agents": ["HR_Agent", "IT_Agent"]
    }

    prompt = USER_PROMPT_TEMPLATE.format(**state)
    print(prompt)

Output Example:
    **YOUR MAIN GOAL:**
    Improve team collaboration

    **WHEN ASKING TRY TO FOLLOW THIS SUBTASK:**
    Analyze team communication barriers

    **Questionnaire:**
    Survey data about team interactions

    **Best Practices:**
    Effective communication practices

    **Additional Context:**
    - Retain the existing analysis and only add your specific input.

    **Current Analysis is a sum of previous analysis previous agents:**
    Previous analysis from HR and IT agents.

    **Questions for the Agent:**
    - What specific barriers prevent collaboration?

    **VERY IMPORTANT**
    **HR_Agent, IT_Agent already provided their analysis, so you can't ask them anymore. Please choose unasked agents instead. IF YOU HAVE ASKED HR, BP, IT, KM and Consulting agents, RETURN Summary_Agent.**

    Respond in the specified structured format. Remember to identify the next agent for the task or indicate if the task is complete.
"""


USER_PROMPT_TEMPLATE = """
    **YOUR MAIN GOAL:**
    {main_task}

    **WHEN ASKING TRY TO FOLLOW THIS SUBTASK:**
    {task}

    **Questionnaire:**
    {questionnaire}

    **Best Practices:**
    {good_practices}

    **Additional Context:**
    - Retain the existing analysis and only add your specific input.

    **Current Analysis is a sum of previous analysis previous agents:**
    {analysis}

    **Questions for the Agent:**
    - {questions}

    **VERY IMPORTANT**
    **{processed_agents} already provided their analysis, so you can't ask them anymore. Please choose unasked agents instead. IF YOU HAVE ASKED HR, BP, IT, KM and Consulting agents, RETURN Summary_Agent.**

    Respond in the specified structured format. Remember to identify the next agent for the task or indicate if the task is complete.
    """