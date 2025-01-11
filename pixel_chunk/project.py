from datetime import datetime
import uuid
from fastapi import APIRouter
from icechunk import Repository, s3_storage
from pydantic.main import BaseModel
import zarr


def create_storage(id: str):
    return s3_storage(
        bucket="pixel-chunk",
        prefix=f"projects/{id}",
        from_env=True,
    )


def create_repo(id: str, rows: int, cols: int, date: datetime) -> Repository:
    storage = create_storage(id)
    repo = Repository.create(storage)
    session = repo.writable_session(branch="main")

    root = zarr.group(store=session.store)
    root.attrs["date_created"] = date.isoformat()
    root.attrs["date_updated"] = date.isoformat()
    root.create_array("pixels", shape=(rows, cols, 4), chunks=(1, 1, 4), dtype="uint8", fill_value=255)
    session.commit("Created project")

    return repo


def get_repo(id: str) -> Repository:
    storage = create_storage(id)
    return Repository.open(storage)


class Project(BaseModel):
    id: str
    date_created: datetime
    date_updated: datetime

    @classmethod
    def create(cls, id: str, rows: int, cols: int):
        now = datetime.utcnow()
        create_repo(id, rows, cols, now)
        return cls(
            id=id,
            date_created=now,
            date_updated=now,
        )


project_router = APIRouter(prefix="/projects")


@project_router.post("/new")
async def new_project(rows: int = 16, cols: int = 16):
    id = str(uuid.uuid4())
    project = Project.create(id, rows, cols)
    return project.dict()
