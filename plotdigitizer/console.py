__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import typing as T
from loguru import logger
import cv2
import numpy as np
import tempfile
import plotdigitizer.core as core
import plotdigitizer.helper as helper
import plotdigitizer.axis

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

@app.command()
def locate_axis(infile: Path):
    """Locate axis.
    """
    img = cv2.imread(str(infile), 0)
    lines = plotdigitizer.axis.find_axis_lines(img)

    img2 = np.zeros_like(img)
    for l in lines:
        helper.draw_line(img2, l)
    helper.display_img(img2)


if __name__ == "__main__":
    app()


def main():
    app()

if __name__ == '__main__':
    main()


