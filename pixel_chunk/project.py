from datetime import datetime, timezone
import logging
from typing import Annotated, cast
import uuid
from cachetools import LRUCache
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from icechunk import IcechunkError, Repository, SnapshotMetadata, s3_storage
from pydantic.main import BaseModel
import zarr
from pixel_chunk.state import COLS_ATTR_KEY, ROWS_ATTR_KEY, DrawState


DATE_CREATED_KEY = "date_created"
DRAWING_ARRAY_KEY = "pixels"
DEFAULT_BRANCH = "main"

repo_cache = LRUCache(5)


def create_storage(id: str):
    return s3_storage(
        bucket="pixel-chunk",
        prefix=f"projects/{id}",
        from_env=True,
    )


def create_repo(id: str, rows: int, cols: int, date: datetime) -> Repository:
    storage = create_storage(id)
    repo = Repository.create(storage)
    session = repo.writable_session(branch=DEFAULT_BRANCH)

    root = zarr.group(store=session.store)
    root.attrs[DATE_CREATED_KEY] = date.isoformat()
    root.create_array(
        DRAWING_ARRAY_KEY,
        shape=(rows * cols, 4),
        chunks=(1, 4),
        dtype="uint8",
        fill_value=255,
        attributes={ROWS_ATTR_KEY: rows, COLS_ATTR_KEY: cols},
    )
    session.commit("Created project")

    return repo


def get_repo(id: str) -> Repository:
    # First check the cache
    repo = repo_cache.get(id, None)
    if repo:
        logging.debug(f"Repo for project {id} found in cache!")
        return repo

    # Otherwise open it and cache it
    try:
        logging.debug(f"Loading repo for project {id}...")
        storage = create_storage(id)
        repo = Repository.open(storage)
        repo_cache[id] = repo
        return repo
    except IcechunkError as e:
        logging.error(f"Failed to open repo for project {id}: {e}")
        raise HTTPException(status_code=404, detail="Project not found")


RepoDep = Annotated[Repository, Depends(get_repo)]


class Project(BaseModel):
    id: str
    date_created: datetime

    @classmethod
    def create(cls, id: str, rows: int, cols: int):
        now = datetime.now(timezone.utc)
        create_repo(id, rows, cols, now)
        return cls(
            id=id,
            date_created=now,
        )


class ProjectVersion(BaseModel):
    id: str
    date: datetime
    message: str

    @classmethod
    def from_snapshot(cls, snapshot: SnapshotMetadata):
        return cls(
            id=snapshot.id,
            date=snapshot.written_at,
            message=snapshot.message,
        )


class ProjectState(BaseModel):
    id: str
    state: DrawState
    versions: list[ProjectVersion]


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
