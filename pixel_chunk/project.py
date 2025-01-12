import uuid
from typing import cast

import zarr
from fastapi import APIRouter, WebSocket

from pixel_chunk.dependencies import RepoDep
from pixel_chunk.state import (
    DEFAULT_BRANCH,
    DRAWING_ARRAY_KEY,
    DrawState,
    Project,
    ProjectState,
    ProjectVersion,
)

project_router = APIRouter(prefix="/projects")


@project_router.post("/new")
async def new_project(rows: int = 16, cols: int = 16):
    id = str(uuid.uuid4())
    project = Project.create(id, rows, cols)
    return project.model_dump()


@project_router.get("/{id}")
async def get_project(repo: RepoDep, id: str, version: str | None = None):
    if not version:
        version = repo.lookup_branch(DEFAULT_BRANCH)
    versions = repo.ancestry(version)
    session = repo.readonly_session(snapshot_id=version)
    root = zarr.open_group(store=session.store, mode="r")
    arr = cast(zarr.Array, root[DRAWING_ARRAY_KEY])
    return ProjectState(
        id=id,
        state=DrawState.from_zarr(arr),
        versions=[
            ProjectVersion.from_snapshot(v)
            for v in versions
            if not v.message.startswith("Repository initialized")
        ],
    ).model_dump()


@project_router.websocket("/{id}/edit")
async def edit_project(websocket: WebSocket, repo: RepoDep):
    # TODO
    pass
