from langgraph.graph import StateGraph, START, END
from .classes import State
from .langgraphNodes import response_node, enrich_query_node,classifier_node, fetch_db_memory, update_db_memory, real_time_knowledge_node, contact_flow_node, forbidden_injection_node, check_limit_node, fetch_context
from .conditionalEdges import conditional_edge_classfier, conditional_edge_pre_checker

graph_builder = StateGraph(State)

graph_builder.add_node("response_node", response_node)
graph_builder.add_node("classifier_node", classifier_node)
graph_builder.add_node("fetch_db_memory", fetch_db_memory)
graph_builder.add_node("check_limit_node", check_limit_node)
graph_builder.add_node("update_db_memory", update_db_memory, defer=True)
graph_builder.add_node("real_time_knowledge_node", real_time_knowledge_node)
graph_builder.add_node("contact_flow_node", contact_flow_node)
graph_builder.add_node("forbidden_injection_node", forbidden_injection_node)
graph_builder.add_node("fetch_context_node", fetch_context)
graph_builder.add_node("rewrite_query_node", enrich_query_node)

graph_builder.add_edge(START, "fetch_db_memory")
graph_builder.add_edge("fetch_db_memory", "check_limit_node")
graph_builder.add_conditional_edges("check_limit_node", conditional_edge_pre_checker)

graph_builder.add_conditional_edges(
    "classifier_node",
    conditional_edge_classfier,
    [
        "response_node",
        "forbidden_injection_node",
        "contact_flow_node",
        "rewrite_query_node",
        END
    ]
)
graph_builder.add_edge("rewrite_query_node", "fetch_context_node")
graph_builder.add_edge("fetch_context_node", "response_node")
graph_builder.add_edge("real_time_knowledge_node", "response_node")
graph_builder.add_edge("response_node", "update_db_memory")
graph_builder.add_edge("forbidden_injection_node", "update_db_memory")
graph_builder.add_edge("contact_flow_node", "update_db_memory")
graph_builder.add_edge("update_db_memory", END)

graph = graph_builder.compile()

