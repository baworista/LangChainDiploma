from langchain_core.messages import SystemMessage
from auth_utils import auth_func
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import sys

auth_func()

from graphSupervisor.graph import graphSupervisor

def main():
    # Check if a CLI parameter (question) is provided
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])  # Combine all CLI arguments into a single string
    else:
        # Default hardcoded question
        question = "Help a multinational manufacturing company in their journey to product management maturity."

    # Invoke the app with the provided or default question
    response = graphSupervisor.invoke({"topic": question}, config={"configurable": {"thread_id": "1"}})

    # Print the report
    print("\n=====REPORT=====")
    print(response["final_report"])

if __name__ == "__main__":
    main()