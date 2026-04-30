from typing import List, TypedDict, Annotated
from pydantic import BaseModel, Field
import operator

# The strict JSON schema for our Silent Evaluator
class EvaluationModel(BaseModel):
    clarity_score: int = Field(description="Score from 1-10 on how clear the answer was.")
    technical_accuracy: int = Field(description="Score from 1-10 on technical correctness.")
    feedback: str = Field(description="One sentence of private feedback on the answer.")
    suggested_probe: str = Field(description="A suggested follow-up topic based on gaps in this answer.")

class InterviewState(TypedDict):
    target_role: str
    focus_area: str
    background: str
    industry_context: str  
    turn_count: int
    transcript: Annotated[List[dict], operator.add] 
    evaluations: Annotated[List[EvaluationModel], operator.add]