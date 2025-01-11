from pydantic import BaseModel
import numpy as np
from zarr import Array


class DrawState(BaseModel):
    chunks: list[str]

    @classmethod
    def from_zarr(cls, arr: Array):
        return cls(chunks=rgba_to_hex(np.array(arr[:])))


class UpdateAction(BaseModel):
    index: int
    color: str

    def apply(self, array: Array):
        """Apply the update action to the source data array."""
        array[self.index] = hex_to_rgba([self.color])[0]


def hex_to_rgba(hex_list: list[str]) -> np.ndarray:
    rgba_array = np.zeros((len(hex_list), 4), dtype=np.uint8)
    for i, hex_color in enumerate(hex_list):
        hex_color = hex_color.lstrip("#")
        rgba_array[i] = [int(hex_color[j : j + 2], 16) for j in (0, 2, 4, 6)] if len(hex_color) == 8 else [int(hex_color[j : j + 2], 16) for j in (0, 2, 4)] + [255]
    return rgba_array


def rgba_to_hex(rgba_array: np.ndarray) -> list[str]:
    hex_list = ["#{:02x}{:02x}{:02x}{:02x}".format(r, g, b, a) for r, g, b, a in rgba_array]
    return hex_list
