from datetime import datetime
from typing import cast
import uuid
from fastapi import APIRouter, HTTPException
from icechunk import IcechunkError, Repository, SnapshotMetadata, s3_storage
from pydantic.main import BaseModel
import zarr
from pixel_chunk.state import COLS_ATTR_KEY, ROWS_ATTR_KEY, DrawState


DATE_CREATED_KEY = "date_created"
DRAWING_ARRAY_KEY = "pixels"
DEFAULT_BRANCH = "main"


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
    storage = create_storage(id)
    return Repository.open(storage)


class Project(BaseModel):
    id: str
    date_created: datetime

    @classmethod
    def create(cls, id: str, rows: int, cols: int):
        now = datetime.utcnow()
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
    return project.dict()


@project_router.get("/{id}")
async def get_project(id: str, version: str | None = None):
    try:
        repo = get_repo(id)
    except IcechunkError:
        raise HTTPException(status_code=404, detail="Project not found")
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
