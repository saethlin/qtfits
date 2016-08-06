import numpy as np
from numpy.lib.stride_tricks import as_strided


def zoom(arr, y_zoom, x_zoom=None):
    if x_zoom is None:
        x_zoom = y_zoom

    if y_zoom == 1 and x_zoom == 1:
        return arr
    elif (y_zoom % 1) == 0 and (x_zoom % 1) == 0:
        r, c = arr.shape
        rs, cs = arr.strides
        new = as_strided(arr, (r, y_zoom, c, x_zoom), (rs, 0, cs, 0))
        return new.reshape(int(r * y_zoom), int(c * x_zoom))
    else:
        y = np.around(np.linspace(0, arr.shape[0]-1, arr.shape[0]*y_zoom)).astype(np.int32)
        x = np.around(np.linspace(0, arr.shape[1]-1, arr.shape[1]*x_zoom)).astype(np.int32)
        y.shape = (-1, 1)
        x.shape = (1, -1)
        coords = [y, x]
        return arr[coords]

if __name__ == '__main__':
    import time
    arr = np.empty((4096, 4096), dtype=np.uint8)
    zoomed = np.empty((4096*8, 4096*8), dtype=np.uint8)

    start = time.time()
    new = zoom(arr, 8)
    print(new.shape)
    print(time.time()-start)

    start = time.time()
    new = zoomed[::2, ::2]
    print(new.shape)
    print(time.time()-start)