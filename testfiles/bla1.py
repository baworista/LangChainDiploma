from typing import List, Sequence

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.constants import END, START
from langgraph.graph import MessageGraph

from auth_utils import auth_func
from testfiles.bla2 import agent_chain, reviewer_chain

auth_func()


def agent_node(state: Sequence[BaseMessage]):
    return agent_chain.invoke({'messages': state})


def reviewer_node(state: Sequence[BaseMessage]) -> List[BaseMessage]:
    rsp = reviewer_chain.invoke({'messages': state})
    return [HumanMessage(content=rsp.content)]


builder = MessageGraph()

builder.add_node('actor', agent_node)
builder.add_node('priest', reviewer_node)
builder.set_entry_point('actor')


def should_continue(state: List[BaseMessage]):
    if len(state) > 6:
        return END
    else:
        return 'priest'


builder.add_edge(START, 'actor')
builder.add_conditional_edges('actor', should_continue)
builder.add_edge('priest', 'actor')

graph = builder.compile()
print(graph.get_graph().draw_mermaid_png())

prompt = HumanMessage(content='Debate about nuklear energy')

responce = graph.invoke(prompt)
print(responce)
