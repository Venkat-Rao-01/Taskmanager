from datetime import date, datetime, time

from fastapi import APIRouter, Depends

from app.database import db
from app.dependencies import get_current_user
from app.models import DashboardOut
from app.routes.tasks import _task_with_names


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardOut)
async def dashboard(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] == "Admin":
        project_query = {}
        task_query = {}
    else:
        project_query = {"members": user["_id"]}
        task_query = {"assignee_id": user["_id"]}

    today_start = datetime.combine(date.today(), time.min)
    total_projects = await db.projects.count_documents(project_query)
    total_tasks = await db.tasks.count_documents(task_query)
    completed_tasks = await db.tasks.count_documents({**task_query, "status": "Done"})
    overdue_tasks = await db.tasks.count_documents({**task_query, "status": {"$ne": "Done"}, "due_date": {"$lt": today_start}})

    statuses = ["To Do", "In Progress", "Review", "Done"]
    by_status = {
        status: await db.tasks.count_documents({**task_query, "status": status})
        for status in statuses
    }
    upcoming = await db.tasks.find({**task_query, "status": {"$ne": "Done"}}).sort("due_date", 1).limit(6).to_list(6)

    return {
        "total_projects": total_projects,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "by_status": by_status,
        "upcoming_tasks": [await _task_with_names(task) for task in upcoming],
    }
