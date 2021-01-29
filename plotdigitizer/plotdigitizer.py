#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Dilawar Singh"
__copyright__ = "Copyright 2017-, Dilawar Singh"
__maintainer__ = "Dilawar Singh"
__email__ = "dilawar.s.rajput@gmail.com"
__status__ = "Development"

import os
import typing as T
import numpy as np
import cv2
from collections import defaultdict
from logruru import logger

windowName_ = "PlotDigitizer"
ix_, iy_ = 0, 0
params_: T.Dict[str, T.Any] = {}

debug_ = False

# Point2d type.
Point2 = T.Tuple[float, float]


def find_center(vec):
    # Find mode of the vector. We do it in following way. We take the bin which
    # has most member and take the mean of the bin.
    # NOTE: This the opencv coordinates. max is min here in y-direction.
    return vec.mean()


def plot_traj(traj):
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    mpl.rcParams["text.usetex"] = False
    x, y = zip(*traj)
    plt.figure()
    plt.subplot(211)
    plt.imshow(img_, interpolation="none", cmap="gray")
    plt.title("Original")
    plt.subplot(212)
    plt.title("Reconstructed")
    plt.plot(x, y)
    plt.tight_layout()
    plt.show()
    plt.close()


def save_debug_imgage(filename, img):
    cv2.imwrite(filename, img)


def click_points(img: np.array, coords: T.List[Point2], event, x, y, flags, params):
    assert img is not None, "No data set"
    # Function to record the clicks.
    r, c = img.shape
    if event == cv2.EVENT_LBUTTONDOWN:
        y = r - y
        logger.info("MOUSE clicked on %s,%s" % (x, y))
        coords.append((x, y))


def show_frame(img, msg="MSG: "):
    global windowName_
    msgImg = np.zeros(shape=(50, img.shape[1]))
    cv2.putText(msgImg, msg, (1, 40), 0, 0.5, 255)
    newImg = np.vstack((img, msgImg))
    cv2.imshow(windowName_, newImg)


def ask_user_to_locate_points(points: T.List[Point2], img: np.array) -> T.List[Point2]:
    coords: T.List[Point2] = []
    cv2.namedWindow(windowName_)
    cv2.setMouseCallback(
        windowName_,
        lambda ev, x, y, flags, params: click_points(
            img, coords, ev, x, y, flags, params
        ),
    )
    while len(coords) < len(points):
        i = len(coords)
        p = points[i]
        pLeft = len(points) - len(coords)
        show_frame(img, "Please click on %s (%d left)" % (p, pLeft))
        if len(coords) == len(points):
            break
        key = cv2.waitKey(1) & 0xFF
        if key == "q":
            break
    logger.info("You clicked %s" % coords)
    return coords


def list_to_points(points) -> T.List[T.List[float]]:
    ps = [[float(a) for a in x.split(",")] for x in points]
    return ps


def compute_scaling_offset(p, P):
    # Currently only linear maps and only 2D.
    px, py = zip(*p)
    Px, Py = zip(*P)
    sX, offX = np.polyfit(px, Px, 1)
    sY, offY = np.polyfit(py, Py, 1)
    return ((sX, sY), (offX, offY))


def findScalingAndPrepareImage(
    img, points: T.List[Point2], coords: T.List[Point2], extra=0
):
    # extra: extra rows and cols to erase. Help in containing error near axis.
    # compute the transformation between old and new axis.
    scalingOffset = compute_scaling_offset(points, coords)
    r, c = img.shape
    # x-axis and y-axis chopping can be computed by offset.
    offX, offY = scalingOffset[1]
    offCols, offRows = int(round(offX)), int(round(offY))
    img[r - offRows - extra :, :] = params_["background"]
    img[:, : offCols + extra] = params_["background"]
    return scalingOffset


def find_trajectory(img, pixel, offset: T.List[Point2], error=0):
    res = []
    r, c = img.shape
    new = np.zeros_like(img)

    # Find all pixels which belongs to a trajectory.
    Y, X = np.where(img == pixel)
    traj = defaultdict(list)
    for x, y in zip(X, Y):
        traj[x].append(y)

    (sX, sY), (offX, offY) = offset
    for k in sorted(traj):
        x = k
        vals = np.array(traj[k])

        # These are in opencv pixles. So there valus starts from the top. 0
        # belogs to top row. Therefore > rather than <.
        vals = vals[np.where(vals > vals.mean())]
        if len(vals) == 0:
            continue

        y = find_center(vals)
        cv2.circle(new, (x, int(y)), 2, 255)
        x1 = (x - offX) / sX
        y1 = (r - y - offY) / sY
        res.append((x1, y1))

    # sort by x-axis.
    res = sorted(res)
    if args_.plot:
        plot_traj(res)
    return res, np.vstack((img, new))


def compute_foregrond_background_stats(img) -> T.Dict[str, T.Any]:
    params = {}
    assert img is not None
    hs, bs = np.histogram(img.ravel(), 256 // 2, [0, 256], density=True)
    hist = sorted(zip(hs, bs), reverse=True)
    # Most often occuring pixel is backgorund. Second most is likely to be
    # primary trajectory.
    params["histogram_binsize2"] = hs
    params["pixel_freq"] = hist
    params["background"] = int(hist[0][1])
    params["foreground"] = int(hist[1][1])
    return params


def process(img):
    global params_
    global args_
    params_ = compute_foregrond_background_stats(img)
    T = findScalingAndPrepareImage(img, extra=args_.erase_near_axis)
    traj, img = find_trajectory(img, int(params_["foreground"]), T)
    save_debug_imgage("final.png", img)
    return traj
