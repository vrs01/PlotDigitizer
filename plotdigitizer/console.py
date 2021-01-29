__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import typing as T
from loguru import logger
import cv2
import tempfile
import plotdigitizer.core as core

import typer
from pathlib import Path

app = typer.Typer()

TEMP_ = Path(tempfile.gettempdir())


@app.command()
def run(
    infile: Path,
    xy: T.List[str] = typer.Option(..., "--xy-on-plot", "-p"),
    px: T.List[str] = typer.Option([], "--px-on-image", "-l"),
    plot: bool = True,
    csvfile: T.Optional[Path] = None,
):
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

    traj = core.process(img, points=points, coords=coords)

    if plot:
        core.plot_traj(traj, img)

    csvfile = Path(f"{infile}.traj.csv") if csvfile is None else csvfile
    with open(csvfile, "w") as f:
        for r in traj:
            f.write("%g %g\n" % (r))
    logger.info("Wrote trajectory to %s" % csvfile)


def main():
    app()
