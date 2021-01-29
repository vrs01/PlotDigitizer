__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

from pathlib import Path
from loguru import logger

import plotdigitizer
import plotdigitizer.core
import plotdigitizer.console

logger.info(f"Calling plotdigitizer from {plotdigitizer.__file__}")


HERE = Path(__file__).parent.resolve()


def test_sanity():
    pngfile = HERE / ".." / "figures" / "trimmed.png"
    assert pngfile.exists(), pngfile
    res = plotdigitizer.console.run(
        pngfile, ["0,0", "20,0", "0,1"], ["22,295", "142,296", "23,215"], plot=False
    )
    print(res)


def main():
    test_sanity()


if __name__ == "__main__":
    main()
