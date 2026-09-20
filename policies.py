from dataclasses import dataclass
from typing import Dict, List, Optional

from .schemas import ActionImpact, DataSensitivity


@dataclass
class AgentPolicy:
    allowed_tools: List[str]
    blocked_tools: List[str]
    allowed_actions: List[str]
    max_data_sensitivity: DataSensitivity
    allowed_destinations: List[str]
    approval_required_tools: List[str]


POLICIES: Dict[str, AgentPolicy] = {
    "investigator": AgentPolicy(
        allowed_tools=["read_file", "search_documents", "create_document", "database_write"],
        blocked_tools=["upload_file", "delete_file", "execute_command"],
        allowed_actions=["read", "search", "write", "create"],
        max_data_sensitivity=DataSensitivity.INTERNAL,
        allowed_destinations=["internal"],
        approval_required_tools=["database_write"],
    ),
    "admin": AgentPolicy(
        allowed_tools=[
            "read_file", "search_documents", "create_document", "database_write", "delete_file"
        ],
        blocked_tools=["execute_command"],
        allowed_actions=["read", "search", "write", "create", "delete"],
        max_data_sensitivity=DataSensitivity.SENSITIVE,
        allowed_destinations=["internal"],
        approval_required_tools=["database_write", "delete_file"],
    ),
}


SENSITIVITY_LEVEL = {
    DataSensitivity.PUBLIC: 0,
    DataSensitivity.INTERNAL: 1,
    DataSensitivity.SENSITIVE: 2,
    DataSensitivity.CRITICAL: 3,
}


def get_policy(agent_id: str) -> Optional[AgentPolicy]:
    return POLICIES.get(agent_id)


def is_tool_allowed(policy: AgentPolicy, tool: str) -> bool:
    if tool in policy.blocked_tools:
        return False
    return tool in policy.allowed_tools


def is_action_allowed(policy: AgentPolicy, action: str) -> bool:
    return action in policy.allowed_actions


def is_data_allowed(
    policy: AgentPolicy, sensitivity: DataSensitivity
) -> bool:
    return SENSITIVITY_LEVEL[sensitivity] <= SENSITIVITY_LEVEL[
        policy.max_data_sensitivity
    ]


def is_destination_allowed(policy: AgentPolicy, destination: str) -> bool:
    return destination in policy.allowed_destinations


def requires_human_approval(policy: AgentPolicy, tool: str) -> bool:
    return tool in policy.approval_required_tools
