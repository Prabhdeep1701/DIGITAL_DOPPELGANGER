from pydantic import BaseModel
from typing import Dict, List, Any, Optional


class ExperimentRequest(BaseModel):
    human_count: int = 100
    bot_count: int = 100
    adversarial_count: int = 100


class ExperimentResult(BaseModel):
    total_sessions: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    false_negative_rate: float
    confusion_matrix: Dict[str, Dict[str, int]]
    per_profile: Dict[str, Dict[str, Any]]
    disclaimer: str = (
        "These results apply to the synthetic/test dataset only and do not "
        "establish real-world bot-detection accuracy."
    )
