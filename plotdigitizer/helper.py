__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import typing as T
import Geometry as G
import cv2
from loguru import logger
from pathlib import Path
import tempfile
import numpy as np
import hashlib


def cache() -> Path:
    c = Path(tempfile.gettempdir()) / "plotdigitizer"
    if not c.isdir():
        c.mkdir(parents=True, exist_ok=True)
    return c


def data_to_hash(data) -> str:
    return hashlib.sha1(data).hexdigest()


def save_img_in_cache(img: np.array, filename: str = ""):
    if not filename:
        filename = f"{data_to_hash(img)}.png"
    outpath = cache() / filename
    cv2.imwrite(str(outpath), img)
    logger.debug(f" Saved to {outpath}")


def show_frame(img, waitfor=10):
    cv2.imshow("FRMAE", img)
    cv2.waitKey(waitfor)


def save_frame(img, filepath: Path):
    cv2.imwrite(str(filepath), img)
    logger.info(f"Written to {filepath}")


def draw_line(img: np.array, line : G.Line, color: int = 128, thickness: int = 2):
    p1, p2 = tuple(map(int,line.A.xy)), tuple(map(int, line.B.xy))
    cv2.line(img, p1, p2, color=color, thickness=thickness)


def display_img(img, outfile: T.Optional[Path] = None):
    import matplotlib.pyplot as plt

    plt.imshow(img, interpolation="none", cmap="gray")
    plt.axis(False)
    if outfile is None:
        plt.show()
        return
    plt.savefig(outfile)
    logger.info(f"Saved to {outfile}")
