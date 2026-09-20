from typing import Dict, List

from .schemas import TaskContext, ToolRequest


TOOL_KEYWORDS: Dict[str, List[str]] = {
    "read_file": [
        "read", "file", "document", "report", "summarize",
        "analyse", "analyze", "review",
    ],
    "search_documents": [
        "search", "find", "document", "information", "report", "lookup",
    ],
    "create_document": [
        "create", "generate", "write", "document", "report", "file", "export", "save",
    ],
    "database_write": [
        "insert", "update", "write", "save", "store", "database", "record",
    ],
    "delete_file": ["delete", "remove", "erase"],
    "upload_file": ["upload", "send", "share", "transfer"],
    "execute_command": ["execute", "command", "run", "shell", "terminal"],
}


def normalize(text: str) -> str:
    return text.lower().strip()


def is_task_relevant(request: ToolRequest, task: TaskContext) -> bool:
    if task.allowed_tools and request.tool not in task.allowed_tools:
        return False

    if (
        task.allowed_destinations
        and request.destination not in task.allowed_destinations
    ):
        return False

    task_text = normalize(task.description)
    keywords = TOOL_KEYWORDS.get(request.tool, [])

    if not keywords:
        return False

    return any(keyword in task_text for keyword in keywords)


def explain_scope_failure(request: ToolRequest, task: TaskContext) -> str:
    return (
        f"Tool '{request.tool}' is outside "
        f"the authorized scope of task '{task.task_id}'."
    )
