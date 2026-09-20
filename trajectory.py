from collections import defaultdict
from typing import Dict, List

from .schemas import ToolRequest


class TrajectoryMonitor:
    def __init__(self):
        self.history: Dict[str, List[ToolRequest]] = defaultdict(list)

    def observe(self, request: ToolRequest) -> None:
        self.history[request.task_id].append(request)

    def get_history(self, task_id: str) -> List[ToolRequest]:
        return self.history.get(task_id, [])

    def detect_anomaly(self, request: ToolRequest) -> tuple[bool, List[str]]:
        history = self.get_history(request.task_id)
        reasons = []
        anomaly_score = 0

        if request.destination == "external":
            if any(r.destination == "internal" for r in history):
                anomaly_score += 5
                reasons.append(
                    "Trajectory changed from internal operations to an external destination."
                )

        if request.impact.value in ["high", "critical"]:
            if any(r.impact.value == "low" for r in history):
                anomaly_score += 5
                reasons.append(
                    "High-impact action appeared after lower-impact operations."
                )

        if request.data_sensitivity.value in ["sensitive", "critical"]:
            if any(
                r.data_sensitivity.value in ["public", "internal"]
                for r in history
            ):
                anomaly_score += 5
                reasons.append(
                    "Sensitive data access appeared after lower-sensitivity operations."
                )

        return anomaly_score > 0, reasons
