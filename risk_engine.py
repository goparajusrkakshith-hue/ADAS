from typing import List, Optional

from .schemas import ActionImpact, DataSensitivity, RiskResult, ToolRequest


class RiskEngine:
    TASK_MISMATCH = 30
    UNAUTHORIZED = 30
    SENSITIVE_DATA = 25
    CRITICAL_DATA = 35
    EXTERNAL_DESTINATION = 20
    MEDIUM_IMPACT = 5
    HIGH_IMPACT = 15
    CRITICAL_IMPACT = 25

    def calculate(
        self,
        request: ToolRequest,
        task_match: bool,
        permission_allowed: bool,
        trajectory_anomaly: bool = False,
        trajectory_reasons: Optional[List[str]] = None,
    ) -> RiskResult:
        score = 0
        reasons = []
        trajectory_reasons = trajectory_reasons or []

        if not task_match:
            score += self.TASK_MISMATCH
            reasons.append(
                "Requested action does not match the current task scope."
            )

        if not permission_allowed:
            score += self.UNAUTHORIZED
            reasons.append(
                "Agent does not have permission for this operation."
            )

        if request.data_sensitivity == DataSensitivity.SENSITIVE:
            score += self.SENSITIVE_DATA
            reasons.append("Sensitive data is involved.")
        elif request.data_sensitivity == DataSensitivity.CRITICAL:
            score += self.CRITICAL_DATA
            reasons.append("Critical data is involved.")

        if request.destination == "external":
            score += self.EXTERNAL_DESTINATION
            reasons.append("Data or action targets an external destination.")

        if request.impact == ActionImpact.MEDIUM:
            score += self.MEDIUM_IMPACT
            reasons.append("Medium-impact operation.")
        elif request.impact == ActionImpact.HIGH:
            score += self.HIGH_IMPACT
            reasons.append("High-impact operation.")
        elif request.impact == ActionImpact.CRITICAL:
            score += self.CRITICAL_IMPACT
            reasons.append("Critical-impact operation.")

        if trajectory_anomaly:
            score += 10
            reasons.extend(trajectory_reasons)

        return RiskResult(score=min(score, 100), reasons=reasons)
