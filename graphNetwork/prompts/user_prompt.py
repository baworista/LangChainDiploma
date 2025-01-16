USER_PROMPT_TEMPLATE = """
    **YOUR MAIN GOAL:**
    {main_task}

    **WHEN ASKING TRY TO FOLLOW THIS SUBTASK:**
    {task}

    **Questionnaire:**
    {questionare}

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