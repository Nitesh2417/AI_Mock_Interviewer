from langgraph.graph import StateGraph, START, END
from src.state import InterviewState
from src.agents import interviewer_agent, evaluator_agent, coach_agent

#Routing logic 
def route_start(state: InterviewState):
    if not state.get("transcript"):
        return "interviewer"
    if state["transcript"][-1]["role"] == "Candidate":
        return "evaluator"
    return "interviewer"

#Routing logic for the interview loop
def route_next_step(state: InterviewState):
    MAX_TURNS = 6
    if state.get("turn_count", 0) >= MAX_TURNS:
        return "coach"
    return "interviewer"

#initialize the graph
builder = StateGraph(InterviewState)


builder.add_node("interviewer", interviewer_agent)
builder.add_node("evaluator", evaluator_agent)
builder.add_node("coach", coach_agent)


builder.add_conditional_edges(START, route_start)

builder.add_conditional_edges(
    "evaluator",
    route_next_step,
    {
        "interviewer": "interviewer",
        "coach": "coach"
    }
)

builder.add_edge("interviewer", END)
builder.add_edge("coach", END)


app_graph = builder.compile()