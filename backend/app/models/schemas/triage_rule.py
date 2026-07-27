"""TriageRule Pydantic v2 Schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.models.triage_rule import RuleLogicOperator


class RuleCondition(BaseModel):
    """A single condition within a triage rule's condition list."""
    node_id: str
    answer_value: str
    negated: bool = False


class TriageRuleCreate(BaseModel):
    symptom_id: str
    severity_level_id: str
    health_concern_id: Optional[str] = None
    rule_name: str = Field(..., min_length=1, max_length=200)
    rule_conditions: List[RuleCondition] = Field(default_factory=list)
    logic_operator: RuleLogicOperator = RuleLogicOperator.AND
    priority_order: int = Field(default=100, ge=1)
    is_red_flag_override: bool = False
    is_active: bool = True
    notes: Optional[str] = None


class TriageRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    symptom_id: str
    severity_level_id: str
    health_concern_id: Optional[str]
    rule_name: str
    rule_conditions: Dict[str, Any]
    logic_operator: RuleLogicOperator
    priority_order: int
    is_red_flag_override: bool
    is_active: bool
    notes: Optional[str]
