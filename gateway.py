from typing import Optional

from .decision_engine import DecisionEngine
from .policies import (
    get_policy,
    is_action_allowed,
    is_data_allowed,
    is_destination_allowed,
    is_tool_allowed,
    requires_human_approval,
)
from .risk_engine import RiskEngine
from .schemas import Decision, SecurityDecision, TaskContext, ToolRequest
from .task_scope import explain_scope_failure, is_task_relevant
from .trajectory import TrajectoryMonitor


class RuntimeSecurityGateway:
    def __init__(
        self,
        trajectory_monitor: Optional[TrajectoryMonitor] = None,
    ):
        self.risk_engine = RiskEngine()
        self.decision_engine = DecisionEngine()
        self.trajectory = trajectory_monitor or TrajectoryMonitor()

    def evaluate(
        self,
        request: ToolRequest,
        task: TaskContext,
    ) -> SecurityDecision:

        reasons = []

        # 1. Agent identity / policy
        policy = get_policy(request.agent_id)

        if policy is None:
            return SecurityDecision(
                decision=Decision.BLOCK,
                risk_score=100,
                reasons=[
                    "Unknown agent identity.",
                    "No security policy exists for this agent.",
                    "Request blocked by fail-closed policy.",
                ],
            )

        # 2. Tool permission
        tool_allowed = is_tool_allowed(policy, request.tool)
        if not tool_allowed:
            reasons.append(
                f"Tool '{request.tool}' is not allowed for this agent."
            )

        # 3. Action permission
        action_allowed = is_action_allowed(policy, request.action)
        if not action_allowed:
            reasons.append(
                f"Action '{request.action}' is not allowed for this agent."
            )

        # 4. Data permission
        data_allowed = is_data_allowed(
            policy, request.data_sensitivity
        )
        if not data_allowed:
            reasons.append(
                "Requested data sensitivity exceeds the agent's permission level."
            )

        # 5. Destination permission
        destination_allowed = is_destination_allowed(
            policy, request.destination
        )
        if not destination_allowed:
            reasons.append(
                f"Destination '{request.destination}' is not allowed."
            )

        # 6. Task scope
        task_match = is_task_relevant(request, task)
        if not task_match:
            reasons.append(explain_scope_failure(request, task))

        permission_allowed = all([
            tool_allowed,
            action_allowed,
            data_allowed,
            destination_allowed,
        ])

        # 7. Trajectory analysis
        trajectory_anomaly, trajectory_reasons = (
            self.trajectory.detect_anomaly(request)
        )

        # 8. Risk calculation
        risk = self.risk_engine.calculate(
            request=request,
            task_match=task_match,
            permission_allowed=permission_allowed,
            trajectory_anomaly=trajectory_anomaly,
            trajectory_reasons=trajectory_reasons,
        )

        # 9. Human approval
        approval_required = requires_human_approval(
            policy, request.tool
        )

        # 10. Final decision
        decision = self.decision_engine.decide(
            risk_score=risk.score,
            permission_allowed=permission_allowed,
            approval_required=approval_required,
            reasons=[*reasons, *risk.reasons],
        )
        if request.request_id:
            decision.request_id = request.request_id

        # 11. Store action in trajectory
        self.trajectory.observe(request)

        return decision
