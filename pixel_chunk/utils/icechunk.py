from datetime import datetime
from icechunk import Repository, s3_storage
import zarr

ROWS_ATTR_KEY = "rows"
COLS_ATTR_KEY = "cols"
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
