from langgraph.graph import StateGraph, START, END
from .classes import State
from .langgraphNodes import response_node, classifier_node, fetch_db_memory, update_db_memory

graph_builder = StateGraph(State)

graph_builder.add_node("response_node", response_node)
graph_builder.add_node("classifier_node", classifier_node)
graph_builder.add_node("fetch_db_memory", fetch_db_memory)
graph_builder.add_node("update_db_memory", update_db_memory)

graph_builder.add_edge(START, "fetch_db_memory")
graph_builder.add_edge("fetch_db_memory", "classifier_node")
graph_builder.add_edge("classifier_node", "response_node")
graph_builder.add_edge("response_node", "update_db_memory")
graph_builder.add_edge("update_db_memory", END)

graph = graph_builder.compile()