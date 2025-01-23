"""
Module: summary_agent_prompt_template

This module defines the template for generating prompts for a summary agent in a multi-agent system.

The `SUMMARY_AGENT_PROMPT_TEMPLATE` is designed for a summary agent whose primary goal is to
compile a comprehensive and actionable executive report. This report synthesizes the analyses
and reviews provided by other agents in the system, adhering to a structured and concise format.

Purpose:
    - Restate the overarching goal of the task.
    - Highlight key findings and analyses from agents.
    - Incorporate questionnaires and best practices.
    - Summarize contributions from agents and identify next steps or unanswered questions.

Template Variables:
    main_task (str): The primary goal or focus of the task being addressed.
    analysis (str): A summary of the findings and analyses provided by agents.
    questionnaire (str): The questionnaire data relevant to the task.
    good_practices (str): Best practices to consider in the analysis.
    processed_agents (str): A list of agents that have already contributed to the task.

Sections of the Prompt:
    1. **Main Goal**: Clarifies the purpose of the summary agent's report.
    2. **Content to Include**:
        - Restate the main goal of the task.
        - Highlight key findings from the agent analyses.
        - Reference questionnaires and best practices.
        - Identify contributing agents and their inputs.
        - Summarize next steps or unresolved issues.
    3. **Guidelines**:
        - Ensure clarity and conciseness in the report.
        - Avoid duplicating prior agent analyses.
        - Focus on actionable insights and recommendations.
    4. **Structured Response Format**: Instructs the agent to follow a specific structure in the report.

Usage Example:
    state = {
        "main_task": "Enhance team collaboration in a multinational organization",
        "analysis": "Key insights from HR and IT agents regarding communication barriers.",
        "questionnaire": "Survey data highlighting pain points in collaboration.",
        "good_practices": "Industry standards for effective team collaboration.",
        "processed_agents": ["HR_Agent", "IT_Agent"],
         }
    prompt = SUMMARY_AGENT_PROMPT_TEMPLATE.format(**state)
    print(prompt)

Output Example:
    **YOUR MAIN GOAL:**
    You are a senior consultant experienced in writing executive reports. Your goal is to write a comprehensive report
    based on the reviews provided by the analyst-reviewer teams.

    The report should be structured, concise, and actionable. It should include an executive summary, an introduction,
    a detailed analysis, and a set of recommendations.

    **WHEN WRITING YOUR SUMMARY, INCLUDE THE FOLLOWING:**
    - Restate the main goal of the task: Enhance team collaboration in a multinational organization.
    - Highlight key findings from the current analysis provided by agents: Key insights from HR and IT agents regarding communication barriers.
    - Here are the questionnaires: Survey data highlighting pain points in collaboration.
    - Here are best practices: Industry standards for effective team collaboration.
    - Mention which agents have already contributed: HR_Agent, IT_Agent.
    - Summarize the next steps or unanswered questions based on the analysis.

    **GUIDELINES:**
    - Be clear and concise.
    - Avoid duplicating prior agent analyses.
    - Provide actionable insights or recommendations if possible.

    **Respond in the specified structured format.**
"""


SUMMARY_AGENT_PROMPT_TEMPLATE = """
    **YOUR MAIN GOAL:**
    You are a senior consultant experienced in writing executive reports. Your goal is to write a comprehensive report based on the reviews provided by the analyst-reviewer teams.

    The report should be structured, concise, and actionable. It should include an executive summary, an introduction, a detailed analysis, and a set of recommendations.   

    **WHEN WRITING YOUR SUMMARY, INCLUDE THE FOLLOWING:**
    - Restate the main goal of the task: {main_task}.
    - Highlight key findings from the current analysis provided by agents: {analysis}.
    - Here are the questionnaires: {questionnaire}.
    - Here are best practices: {good_practices}.
    - Mention which agents have already contributed: {processed_agents}.
    - Summarize the next steps or unanswered questions based on the analysis.

    **GUIDELINES:**
    - Be clear and concise.
    - Avoid duplicating prior agent analyses.
    - Provide actionable insights or recommendations if possible.

    **Respond in the specified structured format.**
"""