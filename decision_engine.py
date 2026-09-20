from typing import List, Optional

from .schemas import Decision, SecurityDecision


class DecisionEngine:
    APPROVAL_THRESHOLD = 31
    BLOCK_THRESHOLD = 61

    def decide(
        self,
        risk_score: int,
        permission_allowed: bool,
        approval_required: bool,
        reasons: Optional[List[str]] = None,
    ) -> SecurityDecision:
        reasons = reasons or []

        if not permission_allowed:
            return SecurityDecision(
                decision=Decision.BLOCK,
                risk_score=risk_score,
                reasons=[*reasons, "Permission check failed."],
            )

        if risk_score >= self.BLOCK_THRESHOLD:
            return SecurityDecision(
                decision=Decision.BLOCK,
                risk_score=risk_score,
                reasons=[
                    *reasons,
                    "Risk score exceeded block threshold.",
                ],
            )

        if approval_required or risk_score >= self.APPROVAL_THRESHOLD:
            return SecurityDecision(
                decision=Decision.HUMAN_APPROVAL,
                risk_score=risk_score,
                reasons=[*reasons, "Human approval required."],
            )

        return SecurityDecision(
            decision=Decision.ALLOW,
            risk_score=risk_score,
            reasons=[*reasons, "Request passed security checks."],
        )
