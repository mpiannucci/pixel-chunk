from datetime import datetime, timezone
from typing import cast
from icechunk import Repository, SnapshotMetadata, s3_storage
from pydantic import BaseModel
import numpy as np
from zarr import Array
import zarr


ROWS_ATTR_KEY = "rows"
COLS_ATTR_KEY = "cols"
DATE_CREATED_KEY = "date_created"
DRAWING_ARRAY_KEY = "pixels"
DEFAULT_BRANCH = "main"


class DrawState(BaseModel):
    chunks: list[str]
    rows: int
    cols: int

    @classmethod
    def from_zarr(cls, arr: Array):
        rows = cast(int, arr.attrs[ROWS_ATTR_KEY])
        cols = cast(int, arr.attrs[COLS_ATTR_KEY])
        return cls(chunks=rgba_to_hex(np.array(arr[:])), rows=rows, cols=cols)


class UpdateAction(BaseModel):
    index: int
    color: str

    def apply(self, array: Array):
        """Apply the update action to the source data array."""
        array[self.index] = hex_to_rgba([self.color])[0]


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


def hex_to_rgba(hex_list: list[str]) -> np.ndarray:
    rgba_array = np.zeros((len(hex_list), 4), dtype=np.uint8)
    for i, hex_color in enumerate(hex_list):
        hex_color = hex_color.lstrip("#")
        rgba_array[i] = (
            [int(hex_color[j : j + 2], 16) for j in (0, 2, 4, 6)]
            if len(hex_color) == 8
            else [int(hex_color[j : j + 2], 16) for j in (0, 2, 4)] + [255]
        )
    return rgba_array


def rgba_to_hex(rgba_array: np.ndarray) -> list[str]:
    hex_list = [
        "#{:02x}{:02x}{:02x}{:02x}".format(r, g, b, a) for r, g, b, a in rgba_array
    ]
    return hex_list


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
