from datetime import datetime, timezone
from typing import cast
from icechunk import SnapshotMetadata
from pydantic import BaseModel
import numpy as np
from zarr import Array

from pixel_chunk.utils.color import hex_to_rgba, rgba_to_hex
from pixel_chunk.utils.icechunk import COLS_ATTR_KEY, ROWS_ATTR_KEY, create_repo


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
