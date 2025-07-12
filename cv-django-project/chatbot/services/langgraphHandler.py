from langgraph.graph import StateGraph, START, END
from .classes import State
from .langgraphNodes import response_node

graph_builder = StateGraph(State)
graph_builder.add_node("response_node", response_node)
graph_builder.add_edge(START, "response_node")
graph_builder.add_edge("response_node", END)
graph = graph_builder.compile()