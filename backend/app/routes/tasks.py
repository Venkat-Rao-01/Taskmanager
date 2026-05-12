from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException, status

from app.database import db
from app.dependencies import get_current_user
from app.models import TaskCreate, TaskOut, TaskUpdate
from app.utils import now_utc, oid, serialize_task


router = APIRouter(prefix="/tasks", tags=["Tasks"])


async def _can_access_project(user: dict, project_id) -> bool:
    if user["role"] == "Admin":
        return True
    project = await db.projects.find_one({"_id": project_id, "members": user["_id"]})
    return project is not None


async def _task_with_names(task: dict) -> dict:
    project = await db.projects.find_one({"_id": task["project_id"]})
    assignee = await db.users.find_one({"_id": task["assignee_id"]})
    return serialize_task(
        task,
        project_name=project["name"] if project else None,
        assignee_name=assignee["name"] if assignee else None,
    )


@router.get("", response_model=list[TaskOut])
async def list_tasks(user: dict = Depends(get_current_user)) -> list[dict]:
    if user["role"] == "Admin":
        query = {}
    else:
        query = {"assignee_id": user["_id"]}
    tasks = await db.tasks.find(query).sort("due_date", 1).to_list(500)
    return [await _task_with_names(task) for task in tasks]


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, user: dict = Depends(get_current_user)) -> dict:
    project_id = oid(payload.project_id)
    assignee_id = oid(payload.assignee_id)
    if not await _can_access_project(user, project_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project access required")

    project = await db.projects.find_one({"_id": project_id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if assignee_id not in project.get("members", []):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee must be a project member")

    task_doc = {
        "title": payload.title.strip(),
        "description": payload.description.strip(),
        "project_id": project_id,
        "assignee_id": assignee_id,
        "creator_id": user["_id"],
        "status": "To Do",
        "priority": payload.priority.value,
        "due_date": datetime.combine(payload.due_date, time.min),
        "created_at": now_utc(),
        "updated_at": now_utc(),
    }
    result = await db.tasks.insert_one(task_doc)
    task_doc["_id"] = result.inserted_id
    return await _task_with_names(task_doc)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(task_id: str, payload: TaskUpdate, user: dict = Depends(get_current_user)) -> dict:
    target_id = oid(task_id)
    task = await db.tasks.find_one({"_id": target_id})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if user["role"] != "Admin" and task["assignee_id"] != user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Task access required")

    updates = payload.model_dump(exclude_unset=True)
    if "assignee_id" in updates:
        updates["assignee_id"] = oid(updates["assignee_id"])
    if "due_date" in updates:
        updates["due_date"] = datetime.combine(updates["due_date"], time.min)
    if "priority" in updates and hasattr(updates["priority"], "value"):
        updates["priority"] = updates["priority"].value
    if "status" in updates and hasattr(updates["status"], "value"):
        updates["status"] = updates["status"].value
    updates["updated_at"] = now_utc()

    await db.tasks.update_one({"_id": target_id}, {"$set": updates})
    updated = await db.tasks.find_one({"_id": target_id})
    return await _task_with_names(updated)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, user: dict = Depends(get_current_user)) -> None:
    task = await db.tasks.find_one({"_id": oid(task_id)})
    if not task:
        return
    if user["role"] != "Admin" and task["creator_id"] != user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins or task creators can delete tasks")
    await db.tasks.delete_one({"_id": task["_id"]})
