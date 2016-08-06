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
        new = as_strided(arr, (r, int(y_zoom), c, int(x_zoom)), (rs, 0, cs, 0))
        return new.reshape(int(r * y_zoom), int(c * x_zoom))
    elif (1/y_zoom % 2) == 0 and (1/x_zoom % 2) == 0:
        return arr[::int(1/y_zoom), ::int(1/x_zoom)]
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
    small = np.empty((1024, 1024), dtype=np.uint8)

    start = time.time()
    new = zoom(arr, 0.125)
    print(time.time()-start)

    start = time.time()
    new2 = arr[::8, ::8]
    print(time.time()-start)