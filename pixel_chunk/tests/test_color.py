from pixel_chunk.state import hex_to_rgba, rgba_to_hex
import numpy as np
import numpy.testing as npt


def test_hex_to_rgb():
    npt.assert_array_equal(hex_to_rgba(['#ff0000ff']), np.array([[255, 0, 0, 255]]))
    npt.assert_array_equal(hex_to_rgba(['#00ff00aa']), np.array([[0, 255, 0, 170]]))
    npt.assert_array_equal(hex_to_rgba(['#0000ff80']), np.array([[0, 0, 255, 128]]))


def test_rgba_to_hex():
    npt.assert_array_equal(rgba_to_hex(np.array([[255, 0, 0, 255]])), ['#ff0000ff'])
    npt.assert_array_equal(rgba_to_hex(np.array([[0, 255, 0, 170]])), ['#00ff00aa'])
    npt.assert_array_equal(rgba_to_hex(np.array([[0, 0, 255, 128]])), ['#0000ff80'])
