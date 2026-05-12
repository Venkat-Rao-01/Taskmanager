from datetime import date, datetime, timezone
from typing import Any

from bson import ObjectId


def oid(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValueError("Invalid id")
    return ObjectId(value)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def serialize_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"],
    }


def serialize_project(project: dict[str, Any], task_count: int = 0, completed_count: int = 0) -> dict[str, Any]:
    return {
        "id": str(project["_id"]),
        "name": project["name"],
        "description": project["description"],
        "owner_id": str(project["owner_id"]),
        "members": [str(member) for member in project.get("members", [])],
        "created_at": project["created_at"],
        "task_count": task_count,
        "completed_count": completed_count,
    }


def serialize_task(task: dict[str, Any], project_name: str | None = None, assignee_name: str | None = None) -> dict[str, Any]:
    due_date = task["due_date"]
    if isinstance(due_date, datetime):
        due_date_value = due_date.date()
    else:
        due_date_value = due_date

    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task["description"],
        "project_id": str(task["project_id"]),
        "project_name": project_name,
        "assignee_id": str(task["assignee_id"]),
        "assignee_name": assignee_name,
        "creator_id": str(task["creator_id"]),
        "status": task["status"],
        "priority": task["priority"],
        "due_date": due_date_value,
        "created_at": task["created_at"],
        "updated_at": task["updated_at"],
        "overdue": due_date_value < date.today() and task["status"] != "Done",
    }
