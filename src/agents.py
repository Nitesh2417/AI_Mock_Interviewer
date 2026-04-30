import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from tavily import TavilyClient

from src.state import InterviewState, EvaluationModel

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
evaluator_llm = llm.with_structured_output(EvaluationModel)

tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None


def load_prompt(filename: str) -> str:
    """
    Helper to load prompts reliably regardless of where the script is executed from.
    This prevents 'FileNotFoundError' if you run the script from outside the root directory.
    """
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(base_dir, "prompts", filename)
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logging.error(f"Missing prompt file: {prompt_path}")
        return ""


def researcher_agent(state: InterviewState):
    """
    Fetches up-to-date industry context using Tavily to ground the interview.
    """
    if not tavily_client:
        return {"industry_context": "Tavily API key missing. Defaulting to general knowledge."}

    query = f"Latest technical interview questions and trends for {state['target_role']} focusing on {state['focus_area']}."
    print(f"Digging up latest industry trends for {state['target_role']}...")
    
    try:
        # Basic search is usually fast enough for this use case
        response = tavily_client.search(query, search_depth="basic", max_results=3)
        context = "\n\n".join([res["content"] for res in response.get("results", [])])
    except Exception as e:
        print(f" Search skipped or failed: {e}")
        context = "No recent industry data available. Default to general best practices."

    return {"industry_context": context}


def interviewer_agent(state: InterviewState):
    prompt_template = load_prompt("interviewer.txt")

    chat_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("transcript", [])])
    
    system_msg = prompt_template.format(
        target_role=state["target_role"],
        focus_area=state["focus_area"],
        background=state["background"],
        industry_context=state.get("industry_context", "None provided."),
        transcript=chat_history
    )
    
    response = llm.invoke([SystemMessage(content=system_msg)])

    return {"transcript": [{"role": "Interviewer", "content": response.content}]}


def evaluator_agent(state: InterviewState):
    transcript = state.get("transcript", [])
    if not transcript or transcript[-1]["role"] != "Candidate":
        return {}

    prompt_template = load_prompt("evaluator.txt")
    
    latest_answer = transcript[-1]["content"]
    latest_question = transcript[-2]["content"] if len(transcript) > 1 else "Opening statement."

    system_msg = prompt_template.format(
        target_role=state["target_role"],
        focus_area=state["focus_area"],
        latest_question=latest_question,
        latest_answer=latest_answer
    )
    
    evaluation = evaluator_llm.invoke([SystemMessage(content=system_msg)])
    
    return {"evaluations": [evaluation]}


def coach_agent(state: InterviewState):
    prompt_template = load_prompt("coach.txt")
    
    chat_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state.get("transcript", [])])
    
    evals = state.get("evaluations", [])
    formatted_evals = "\n".join([str(e.model_dump()) for e in evals]) if evals else "No evaluations recorded."
    
    system_msg = prompt_template.format(
        target_role=state["target_role"],
        transcript=chat_history,
        evaluations=formatted_evals
    )
    
    response = llm.invoke([SystemMessage(content=system_msg)])
    
    return {"transcript": [{"role": "Coach", "content": response.content}]}
