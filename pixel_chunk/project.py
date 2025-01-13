import uuid
from typing import Union, cast

from icechunk import (
    ConflictDetector,
    ConflictError,
    RebaseFailedError,
    Repository,
    Session,
)
import zarr
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from pixel_chunk.dependencies import RepoDep
from pixel_chunk.state import (
    CommitCommand,
    CommitConflicts,
    CommitSuccess,
    DrawState,
    Project,
    ProjectState,
    ProjectVersion,
    RebaseCommitCommand,
)
from pixel_chunk.utils.icechunk import DEFAULT_BRANCH, DRAWING_ARRAY_KEY


class SessionManager:
    sessions: dict[WebSocket, Session] = {}

    async def connect(self, ws: WebSocket, repo: Repository):
        await ws.accept()
        session = repo.writable_session(DEFAULT_BRANCH)
        self.sessions[ws] = session

    def try_commit(
        self, ws: WebSocket, commit: CommitCommand
    ) -> CommitSuccess | CommitConflicts:
        session = self.sessions[ws]
        commit.apply(session=session)

        # Check for conflicts
        try:
            session.rebase(ConflictDetector())
            commit_id = session.commit(commit.message)
            return CommitSuccess(latest_snapshot=commit_id)
        except RebaseFailedError as e:
            failed_at_snapshot_id = e.snapshot_id

            # We are only messing with chunks, so only chunks can have conflicts.
            # Plus we know that we only care about the root indice of the chunk for now, latest
            # we could mix colors or something haha
            conflicted_chunks = [
                chunk[0] for c in e.conflicts for chunk in c.conflicted_chunks
            ]
            return CommitConflicts(
                source_snapshot=session.snapshot_id,
                failed_at_snapshot=failed_at_snapshot_id,
                conflicted_chunks=conflicted_chunks,
            )

    def try_rebase_commit(
        self, ws: WebSocket, commit: RebaseCommitCommand
    ) -> CommitSuccess | CommitConflicts:
        session = self.sessions[ws]
        resolver = commit.resolver

        try:
            session.rebase(resolver)
            commit_id = session.commit(commit.message)
            return CommitSuccess(latest_snapshot=commit_id)
        except RebaseFailedError as e:
            failed_at_snapshot_id = e.snapshot_id
            conflicted_chunks = [
                chunk[0] for c in e.conflicts for chunk in c.conflicted_chunks
            ]
            return CommitConflicts(
                source_snapshot=session.snapshot_id,
                failed_at_snapshot=failed_at_snapshot_id,
                conflicted_chunks=conflicted_chunks,
            )

    def disconnect(self, ws: WebSocket):
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
            try:
                command = CommitCommand.model_validate_json(raw_data)
                result = session_manager.try_commit(websocket, command)
            except Exception:
                command = RebaseCommitCommand.model_validate_json(raw_data)
                result = session_manager.try_rebase_commit(websocket, command)
            await websocket.send_json(result.model_dump())
    except WebSocketDisconnect:
        session_manager.disconnect(websocket)
