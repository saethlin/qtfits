import numpy as np


def zoom(arr, *factors):
    if len(factors) == 1:
        y_zoom = factors[0]
        x_zoom = factors[0]
    else:
        y_zoom = factors[0]
        x_zoom = factors[1]
    if y_zoom == 1 and x_zoom == 1:
        new = arr
    elif y_zoom > 1 and x_zoom > 1:
        factor = int(y_zoom)
        new = np.empty(tuple(np.array(arr.shape)*factor), arr.dtype)
        for x in range(factor):
            for y in range(factor):
                new[x::factor, y::factor] = arr
    else:
        y = np.around(np.linspace(0, arr.shape[0]-1, arr.shape[0]*y_zoom)).astype(np.int32)
        x = np.around(np.linspace(0, arr.shape[1]-1, arr.shape[1]*x_zoom)).astype(np.int32)
        y.shape = (-1, 1)
        x.shape = (1, -1)
        coords = [y, x]
        new = arr[coords]

    return new
