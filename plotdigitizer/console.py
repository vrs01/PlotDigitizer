__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import typing as T
from loguru import logger
import cv2
import numpy as np
import itertools
import tempfile
import plotdigitizer.core as core
import math

import typer
from pathlib import Path

app = typer.Typer()

TEMP_ = Path(tempfile.gettempdir())

def show_frame(img, delay=10):
    cv2.imshow('Frame', img)
    cv2.waitKey(delay)

def save_frame(img, outfile: Path):
    cv2.imwrite(str(outfile), img)

@app.command()
def run(
    infile: Path,
    xy: T.List[str] = typer.Option(..., "--xy-on-plot", "-p"),
    px: T.List[str] = typer.Option([], "--px-on-image", "-l"),
    plot: bool = True,
    csvfile: T.Optional[Path] = None,
) -> T.List[core.Point2]:
    global TEMP_
    logger.info("Got file: %s" % infile)
    img = cv2.imread(str(infile), cv2.IMREAD_GRAYSCALE)
    core.save_debug_imgage(TEMP_ / "_original.png", img)

    points = core.list_to_points(xy)
    coords = core.list_to_points(px)

    if len(coords) != len(points):
        logger.debug(
            "Either location is not specified or their numbers don't"
            " match with given xy."
        )
        core.ask_user_to_locate_points(points, img)
    else:
        # User specified coordinates are in opencv axis i.e. top-left is 0,0
        yoffset = img.shape[0]
        coords = [(x, yoffset - y) for (x, y) in coords]

    traj = core.compute_trajectory(img, points=points, coords=coords)

    if plot:
        core.plot_traj(traj, img)

    if csvfile is not None:
        with open(csvfile, "w") as f:
            for r in traj:
                f.write("%g %g\n" % (r))
        logger.info("Wrote trajectory to %s" % csvfile)
    return traj

def angle(line1, line2):
    x1, y1, x2, y2 = line1
    m1 = math.atan2(y1-y2, x1-x2)
    x1, y1, x2, y2 = line2
    m2 = math.atan2(y1-y2, x1-x2)
    return int((m1 - m2) / math.pi * 180)

def find_axis_lines(img):
    edges = cv2.Canny(img, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 120, minLineLength=200, maxLineGap=100)
    N = len(lines)
    res = []
    for i in range(N):
        for ii in range(i, N):
            l1, l2 = lines[i][0], lines[ii][0]
            th = angle(l1, l2)
            if abs(th - 90) < 5:
                res.append(l1)
                res.append(l2)
    return res

@app.command()
def feeling_lucky(imgfile: Path):
    assert imgfile.exists()
    logger.info(f'Reading {imgfile}')
    img = cv2.imread(str(imgfile), 0)
    lines = find_axis_lines(img)
    img1 = np.zeros_like(img)
    for line in lines:
        x1, y1, x2, y2 = line
        print(x1, y1, x2, y2)
        cv2.line(img1, (x1, y1), (x2, y2), 150, 2)

    save_frame(img1, 'temp.png')




if __name__ == '__main__':
    app()


