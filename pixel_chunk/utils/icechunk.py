import io
from datetime import datetime
from typing import cast

import zarr
from icechunk import Repository, s3_storage
from PIL import Image

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


def array_to_image_bytes(arr: zarr.Array, scale = 1) -> io.BytesIO:
    rows = cast(int, arr.attrs[ROWS_ATTR_KEY])
    cols = cast(int, arr.attrs[COLS_ATTR_KEY])
    reshaped = arr[:].reshape(rows, cols, 4)

    image = Image.fromarray(reshaped, mode="RGBA")
    if scale > 1:
        image = image.resize((cols * scale, rows * scale), Image.NEAREST)

    image_buffer = io.BytesIO()
    image.save(image_buffer, format="PNG")
    image_buffer.seek(0)
    return image_buffer
