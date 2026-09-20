from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Decision(str, Enum):
    ALLOW = "ALLOW"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"
    BLOCK = "BLOCK"


class DataSensitivity(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"
    CRITICAL = "critical"


class ActionImpact(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ToolRequest(BaseModel):
    agent_id: str
    task_id: str
    tool: str
    action: str
    resource: Optional[str] = None
    data_sensitivity: DataSensitivity = DataSensitivity.INTERNAL
    destination: str = "internal"
    impact: ActionImpact = ActionImpact.LOW
    parameters: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None


class TaskContext(BaseModel):
    task_id: str
    description: str
    allowed_tools: List[str] = Field(default_factory=list)
    allowed_destinations: List[str] = Field(default_factory=list)


class RiskResult(BaseModel):
    score: int
    reasons: List[str] = Field(default_factory=list)


class SecurityDecision(BaseModel):
    decision: Decision
    risk_score: int
    reasons: List[str] = Field(default_factory=list)
    request_id: Optional[str] = None
