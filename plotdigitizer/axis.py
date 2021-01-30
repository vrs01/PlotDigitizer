# -*- coding: utf-8 -*-

__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import plotdigitizer.numutil as numutil
import plotdigitizer.helper as helper
import cv2
import typing as T
import numpy as np
import Geometry as G
from loguru import logger

import typer

app = typer.Typer()


def toLine(pts) -> G.Line:
    assert len(pts) == 4
    return G.Line(list(pts[:2]), list(pts[2:]))


def find_axis_lines(img: np.array) -> T.List[G.Line]:
    """Try to find axis lines."""
    h, w = img.shape
    img = numutil.normalize_image(img)

    logger.info(f" shape {img.shape}")
    edges = cv2.Canny(img, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        200,
        minLineLength=min(h,w)//5,
        maxLineGap=5,
    )
    assert len(lines) > 0, "No lines found"
    N = len(lines)
    res = []
    for i in range(N):
        for ii in range(i, N):
            l1, l2 = toLine(lines[i][0]), toLine(lines[ii][0])
            try:
                th = l1.degreesBetween(l2)
            except Exception as e:
                logger.warning(
                    f"Failed to compute angle between {l1} and {l2}. Error {e}"
                )
                continue
            # Select almost perpendicular lines.
            if abs(th - 90) <= 3:
                res.append(l1)
                res.append(l2)
    assert len(res) > 0
    return res
