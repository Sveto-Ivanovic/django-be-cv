from .classes import State
from langgraph.graph import StateGraph, START, END

def conditional_edge_classfier(state: State):
    classifier = state.get("classifier") or []
    has_vector_db = state["supabase_metadata"] or state["pinecone_metadata"]

    if len(classifier) == 0 or not any(c in classifier for c in ["forbidden_injection", "contact_flow", "real_time_knowledge"]):
        if has_vector_db:
            return "rewrite_query_node"
        return "response_node"

    if "forbidden_injection" in classifier:
        return "forbidden_injection_node"

    if "contact_flow" in classifier:
        if state["llm_config"]["agent_contact_flow"]["enabled"] and has_vector_db:
            return ["contact_flow_node", "rewrite_query_node"]
        if state["llm_config"]["agent_contact_flow"]["enabled"] and not has_vector_db:
            return ["contact_flow_node", "response_node"]
        if has_vector_db:
            return "rewrite_query_node"
        return "response_node"
    
    
    # if "real_time_knowledge" in state["classifier"] and "contact_flow" in state["classifier"]:
    #     if state["llm_config"]["agent_real_time_knowledge_flow"]["enabled"] and state["llm_config"]["agent_contact_flow"]["enabled"]:
    #         return ["real_time_knowledge_node", "contact_flow_node"]    
    #     elif state["llm_config"]["agent_real_time_knowledge_flow"]["enabled"]:
    #         return "real_time_knowledge_node"
    #     elif state["llm_config"]["agent_contact_flow"]["enabled"]:
    #         return "contact_flow_node"
    #     else:
    #         return "response_node"
    
    # if "real_time_knowledge" in state["classifier"]:
    #     if state["llm_config"]["agent_real_time_knowledge_flow"]["enabled"]:
    #         return "real_time_knowledge_node"
    #     else:
    #         return "response_node"  
    

def conditional_edge_pre_checker(state: State):
    if state["limit_exceeded"]:
        return END
    else:
        return "classifier_node"
