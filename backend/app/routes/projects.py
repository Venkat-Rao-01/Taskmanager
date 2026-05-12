from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import db
from app.dependencies import get_current_user, require_admin
from app.models import ProjectCreate, ProjectOut, ProjectUpdate
from app.utils import now_utc, oid, serialize_project


router = APIRouter(prefix="/projects", tags=["Projects"])


async def _project_stats(project_id: ObjectId) -> tuple[int, int]:
    total = await db.tasks.count_documents({"project_id": project_id})
    completed = await db.tasks.count_documents({"project_id": project_id, "status": "Done"})
    return total, completed


@router.get("", response_model=list[ProjectOut])
async def list_projects(user: dict = Depends(get_current_user)) -> list[dict]:
    if user["role"] == "Admin":
        query = {}
    else:
        query = {"members": user["_id"]}
    projects = await db.projects.find(query).sort("created_at", -1).to_list(200)
    output = []
    for project in projects:
        total, completed = await _project_stats(project["_id"])
        output.append(serialize_project(project, total, completed))
    return output


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, user: dict = Depends(require_admin)) -> dict:
    member_ids = {user["_id"]}
    for member_id in payload.member_ids:
        member_ids.add(oid(member_id))

    project_doc = {
        "name": payload.name.strip(),
        "description": payload.description.strip(),
        "owner_id": user["_id"],
        "members": list(member_ids),
        "created_at": now_utc(),
    }
    result = await db.projects.insert_one(project_doc)
    project_doc["_id"] = result.inserted_id
    return serialize_project(project_doc)


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(project_id: str, payload: ProjectUpdate, _: dict = Depends(require_admin)) -> dict:
    target_id = oid(project_id)
    updates = payload.model_dump(exclude_unset=True)
    if "member_ids" in updates:
        updates["members"] = [oid(member_id) for member_id in updates.pop("member_ids")]
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No updates provided")

    await db.projects.update_one({"_id": target_id}, {"$set": updates})
    project = await db.projects.find_one({"_id": target_id})
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    total, completed = await _project_stats(project["_id"])
    return serialize_project(project, total, completed)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, _: dict = Depends(require_admin)) -> None:
    target_id = oid(project_id)
    await db.projects.delete_one({"_id": target_id})
    await db.tasks.delete_many({"project_id": target_id})
