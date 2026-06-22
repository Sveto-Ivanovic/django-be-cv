from .classes import State
from langgraph.graph import StateGraph, START, END

def conditional_edge_classfier(state: State):
    if len(state["classifier"]) == 0:
        return "response_node"
    
    if "forbidden_injection" in state["classifier"]:
        return "forbidden_injection_node"
    
    if "real_time_knowledge" in state["classifier"] and "contact_flow" in state["classifier"]:
        if state["llm_config"]["agent_real_time_knowledge_flow"]["enabled"] and state["llm_config"]["agent_contact_flow"]["enabled"]:
            return ["real_time_knowledge_node", "contact_flow_node"]    
        elif state["llm_config"]["agent_real_time_knowledge_flow"]["enabled"]:
            return "real_time_knowledge_node"
        elif state["llm_config"]["agent_contact_flow"]["enabled"]:
            return "contact_flow_node"
        else:
            return "response_node"
    
    if "real_time_knowledge" in state["classifier"]:
        if state["llm_config"]["agent_real_time_knowledge_flow"]["enabled"]:
            return "real_time_knowledge_node"
        else:
            return "response_node"  
    
    if "contact_flow" in state["classifier"]:
        if state["llm_config"]["agent_contact_flow"]["enabled"]:
            return ["contact_flow_node", "response_node"]
        else:
            return "response_node"


def conditional_edge_pre_checker(state: State):
    if state["limit_exceeded"]:
        return END
    else:
        return "classifier_node"
