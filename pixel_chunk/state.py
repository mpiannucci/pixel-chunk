from datetime import datetime, timezone
from typing import Literal, cast
from icechunk import BasicConflictSolver, Session, SnapshotInfo, VersionSelection
from pydantic import BaseModel
import numpy as np
import zarr

from pixel_chunk.utils.color import hex_to_rgba, rgba_to_hex
from pixel_chunk.utils.icechunk import (
    COLS_ATTR_KEY,
    DRAWING_ARRAY_KEY,
    ROWS_ATTR_KEY,
    create_repo,
)


class DrawState(BaseModel):
    chunks: list[str]
    rows: int
    cols: int

    @classmethod
    def from_zarr(cls, arr: zarr.Array):
        rows = cast(int, arr.attrs[ROWS_ATTR_KEY])
        cols = cast(int, arr.attrs[COLS_ATTR_KEY])
        return cls(chunks=rgba_to_hex(np.array(arr[:])), rows=rows, cols=cols)


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
    def from_snapshot(cls, snapshot: SnapshotInfo):
        return cls(
            id=snapshot.id,
            date=snapshot.written_at,
            message=snapshot.message,
        )


class ProjectState(BaseModel):
    id: str
    state: DrawState
    versions: list[ProjectVersion]


class UpdateAction(BaseModel):
    index: int
    color: str

    def apply(self, array: zarr.Array):
        """Apply the update action to the source data array."""
        array[self.index] = hex_to_rgba([self.color])[0]


class CommitCommand(BaseModel):
    message: str
    changes: list[UpdateAction]

    def apply(self, session: Session):
        """Apply the commit to the session"""
        root = zarr.open_group(session.store, mode="a")
        arr = cast(zarr.Array, root[DRAWING_ARRAY_KEY])
        for change in self.changes:
            arr[change.index] = hex_to_rgba([change.color])[0]


class RebaseCommitCommand(BaseModel):
    message: str
    strategy: Literal["ours"] | Literal["theirs"]

    @property
    def resolver(self) -> BasicConflictSolver:
        if self.strategy == "ours":
            chunk_selection = VersionSelection.UseOurs
        else:
            chunk_selection = VersionSelection.UseTheirs
        return BasicConflictSolver(on_chunk_conflict=chunk_selection)


class CommitSuccess(BaseModel):
    latest_snapshot: str


class CommitConflicts(BaseModel):
    source_snapshot: str
    failed_at_snapshot: str
    conflicted_chunks: list[int]
