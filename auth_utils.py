import os
import getpass
from dotenv import load_dotenv

def auth_func():
    """
    A function to set environment variables required for authentication.
    Loads variables from .env file and prompts for missing ones.
    """

    # Load environment variables from .env file
    load_dotenv()

    def _set_env(var: str, prompt_message: str = None):
        """
        Sets an environment variable if it's not already set.
        Prompts the user for input if the variable is missing.

        Args:
            var (str): The name of the environment variable.
            prompt_message (str): Custom message to display when prompting for input.
        """
        if not os.environ.get(var):
            prompt_message = prompt_message or f"{var}: "
            os.environ[var] = getpass.getpass(prompt_message)

    # Prompt for required API keys
    _set_env("OPENAI_API_KEY", "Please enter your OpenAI API key: ")
    _set_env("LANGCHAIN_API_KEY", "Please enter your LangChain API key: ")

    # Set additional environment variables
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_PROJECT", "langchain-academy")

    print("Environment variables set successfully.")
