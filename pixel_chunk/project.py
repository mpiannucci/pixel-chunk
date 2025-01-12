import uuid
from typing import cast

from icechunk import Repository, Session
import zarr
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from pixel_chunk.dependencies import RepoDep
from pixel_chunk.state import (
    CommitCommand,
    CommitSuccess,
    DrawState,
    Project,
    ProjectState,
    ProjectVersion,
)
from pixel_chunk.utils.icechunk import DEFAULT_BRANCH, DRAWING_ARRAY_KEY


class SessionManager:
    sessions: dict[WebSocket, Session] = {}

    async def connect(self, ws: WebSocket, repo: Repository):
        await ws.accept()
        session = repo.writable_session(DEFAULT_BRANCH)
        self.sessions[ws] = session

    def try_commit(self, ws: WebSocket, commit: CommitCommand) -> CommitSuccess:
        session = self.sessions[ws]
        commit_id = commit.apply(session=session)
        return CommitSuccess(latest_snapshot=commit_id)

    async def disconnect(self, ws: WebSocket):
        del self.sessions[ws]


session_manager = SessionManager()


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
    await session_manager.connect(websocket, repo)
    try:
        while True:
            raw_data = await websocket.receive_text()
            command = CommitCommand.model_validate_json(raw_data)
            result = session_manager.try_commit(websocket, command)
            await websocket.send_json(result.model_dump())
    except WebSocketDisconnect:
        session_manager.disconnect(websocket)
