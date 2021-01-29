__author__ = "Dilawar Singh"
__email__ = "dilawar@subcom.tech"

import plotdigitizer.core
from PIL import Image, ImageTk
from pathlib import Path
from loguru import logger
import typing as T

import PySimpleGUI as sg

here_ = Path(__file__).parent.resolve()

# TkId type
TkId = int

w_, h_ = 1200, 1200
try:
    from screeninfo import get_monitors

    m = get_monitors()[0]
    w_, h_ = int(m.width // 2.5), int(m.height // 2)
    logger.info(f" Heigh {h_}, width {w_}")
except Exception as e:
    logger.warning("module screeninfo is not available: %s" % e)
    pass

default_img_ = here_ / "data" / "pnas-koshland.png"


class Point:
    def __init__(self, point, canvas, label="", color="black", size=5):
        self.point: T.Tuple[float, float] = point
        self.canvas = canvas
        self.label: str = label
        self.tkpt: TkId = self.canvas.DrawPoint(self.point, color=color, size=size)
        if self.label:
            self.tkid2 = self.draw_label(self.label)

    def draw_label(self, label, color='blue'):
        loc = list(self.point)
        if label[0] == 'x':
            loc[0] -= 0
            loc[1] -= 30
        else:
            loc[0] -= 30
            loc[1] -= 0
        return self.canvas.draw_text(label, location=loc, color=color)

    def erase(self):
        logger.info(f" Deleting point {self.tkpt} {self.point}")
        self.canvas.DeleteFigure(self.tkpt)
        self.canvas.DeleteFigure(self.tkid2)
        self.canvas.update()
        self.tkpt = None
        self.tkpt2 = None


class Line:
    def __init__(self, p1, p2, canvas, *, color: str = "blue", width: int = 2):
        self.p1 = p1
        self.p2 = p2
        self.canvas = canvas
        self.tkid: TkId = self.canvas.DrawLine(p1, p2, color=color, width=width)

    def erase(self):
        self.canvas.DeleteFigure(self.tkid)
        self.tkid = 0


class AxisLine(Line):
    def __init__(self, p1, p2, axis: str, canvas, *, color="blue", width=2):
        w, h = canvas.CanvasSize
        p1, p2 = list(p1), list(p2)
        if axis == "x":
            p1[0] = 0
            p2[0] = w
        if axis == "y":
            p1[1] = 0
            p2[1] = h
        super().__init__(p1, p2, canvas, color=color, width=width)


class Axes:
    def __init__(self, canvas, window=None):
        self.canvas = canvas
        self.window = window
        self.lines: T.Dict[str, T.Optional[Line]] = dict(x=None, y=None)
        self.points: T.Dict[str, T.List[Point]] = dict(x=[], y=[])

    def erase(self, which: str):
        l = self.lines[which]
        if l is not None:
            l.erase()
        self.lines[which] = None

        for p in self.points[which]:
            p.erase()
        self.points[which] = []

    def add_axis_point(self, pt, color="red"):
        logger.info(f" Adding point {pt=}")
        if len(self.points["x"]) < 2:
            p = Point(
                pt,
                canvas=self.canvas,
                color="red",
                size=10,
                label=f"x{len(self.points['x'])}",
            )
            self.points["x"].append(p)
        else:
            p = Point(
                pt,
                canvas=self.canvas,
                color="red",
                size=10,
                label=f"y{len(self.points['y'])}",
            )
            self.points["y"].append(p)

        try:
            txtelem = self.window[p.label]
            txtelem.update(value=f"{p.label}={p.point}")
        except Exception:
            logger.warning(f"{p.label} not found.")

        if len(self.points["x"]) > 1 or len(self.points["y"]) > 1:
            self.update_axis()

    def update_axis(self, color="blue"):
        # update x-axis
        logger.info("Drawing axes")
        for axis in ["x", "y"]:
            pts = self.points[axis]
            if len(pts) < 2:
                continue
            assert pts, f"No points found for {axis}"
            logger.info(f" Axis {axis} is defined by {pts}")
            p1, p2 = pts
            self.lines[axis] = AxisLine(
                p1.point, p2.point, axis, self.canvas, width=2, color=color
            )
            logger.info(f" Axis {axis} is drawn")


class GUI:
    def __init__(self):
        self.photo = None
        self.canvas_size = (w_, h_)
        self.canvas = sg.Graph(
            (w_, h_),
            graph_bottom_left=(0, 0),
            graph_top_right=(w_, h_),
            background_color="ivory",
            float_values=True,
            border_width=2,
            # drag_submits=True,
            enable_events=True,
            key="-GRAPH-",
        )

        size1 = (15, 1)
        size2 = (10, 1)
        self.settings = sg.Column(
            [
                [sg.T("Background"), sg.Input(key="background", size=(10, 1))],
                [sg.T("Foreground"), sg.Input(key="foreground", size=(10, 1))],
                [sg.HorizontalSeparator()],
                # These are updated when points are added.
                [
                    sg.T("x0", key="x0", size=size1),
                    sg.Input(key="x0val", size=size2),
                ],
                [
                    sg.T("x1", key="x1", size=size1),
                    sg.Input(key="x1val", size=size2),
                ],
                [sg.Button("Clear X-axis")],
                [sg.HorizontalSeparator()],
                [
                    sg.T("y0", key="y0", size=size1),
                    sg.Input(key="y0val", size=size2),
                ],
                [
                    sg.T("y1", key="y1", size=size1),
                    sg.Input(key="y1val", size=size2),
                ],
                [sg.Button("Clear Y-axis")],
                [sg.HorizontalSeparator()],
                [sg.Button("Extract Data")],
            ]
        )
        self.canvas_image = None
        self.layout = [
            [
                sg.Text("Image (URL or location)"),
                sg.Input(key="location"),
                sg.FileBrowse(),
                sg.Button("Load"),
            ],
            [self.canvas, self.settings],
            [sg.Button("Ok"), sg.Cancel()],
        ]
        self.window = sg.Window(
            "Plot Digitizer",
            self.layout,
            # return_keyboard_events=True,
            finalize=True,
        )
        self.window.set_cursor("arrow")
        self.canvas.bind("<Enter>", "+MOUSE OVER+")
        self.canvas.bind("<Leave>", "+MOUSE AWAY+")
        self.canvas.bind("<Shift-L>", "+Shift+")
        self.canvas.bind("<Shift-R>", "+Shift+")
        self.points = dict(x=[], y=[], z=[])
        self.axes: Axes = Axes(canvas=self.canvas, window=self.window)

    def draw_grid(self, color="lightgray", x=True, y=True, step: int = 20):
        w, h = self.canvas_size
        if y:
            for _w in range(0, w, step):
                self.canvas.draw_line((_w, 0), (_w, h), color=color)
        if x:
            for _h in range(0, h, step):
                self.canvas.draw_line((0, _h), (w, _h), color=color)

    def load_image(self, imgfile: Path, offset_w=0, offset_h=0):
        self.curimage = imgfile
        tkcanvas = self.canvas.TKCanvas
        im = Image.open(imgfile)
        self.photo = ImageTk.PhotoImage(image=im)
        imsize = im.size
        if imsize > self.canvas_size:
            logger.info("Image is large. Resizing figure to {self.canvas_size}")
            im.resize(self.canvas_size)
        imw, imh = im.size
        self.canvas_image = tkcanvas.create_image(
            20+offset_w,
            self.canvas_size[1] - imh - offset_h - 20,
            image=self.photo,
            anchor="nw",
        )
        self.draw_grid()

    def move_image(self, dw, dh):
        logger.info(f"moving {dw=} {dh=}")
        assert self.canvas_image
        assert self.canvas
        self.canvas.MoveFigure(self.canvas_image, -dw, -dh)

    def run(self):
        # load the default figure
        self.load_image(default_img_)
        drags = []
        while True:  # the event loop
            event, values = self.window.read()
            logger.info(f"{event=} {values}")
            if event == sg.WIN_CLOSED:
                break
            if event == "Cancel":
                break
            elif event == "Ok":
                pass
            elif event == "-GRAPH-+MOUSE OVER+":
                self.window.set_cursor("crosshair")
            elif event == "-GRAPH-+MOUSE AWAY+":
                self.window.set_cursor("arrow")
            elif event == "Load":
                assert self.window["Browse"] or self.window["location"]
                filepath = Path(self.window["location"].get())
                self.load_image(filepath)
            elif event == "-GRAPH-":
                pt = values["-GRAPH-"]
                self.axes.add_axis_point(pt)
                # drags.append(pt)
                # if len(drags) > 2:
                #     frm, to = drags[-2], drags[-1]
                #     dw, dh = tuple(map(lambda a, b: a - b, frm, to))
                #     if dw > 0 or dh > 0:
                #         self.move_image(dw, dh)
                #     else:
                #         # no point keeping this point.
                #         drags.pop()
            elif event == "-GRAPH-+UP":
                if self.points and self.points[0]:
                    logger.info(f"Locating {self.locatePoint}")
                logger.info("Done dragging")
            elif "Clear X-axis" in event:
                logger.info("Clearing all x-axis.")
                self.axes.erase("x")
            elif "Clear Y-axis" in event:
                logger.info("Clearing all points y-axis")
                self.axes.erase("y")
            elif "Locate" in event:
                whichPoint = int(event[-1])
                assert whichPoint in [0, 1, 2]
                xkey, ykey = f"x{whichPoint}", f"y{whichPoint}"
                x, y = None, None
                self.window.set_cursor("crosshair")
                try:
                    x, y = float(values[xkey]), float(values[ykey])
                    self.locatePoint = x, y
                    logger.info(f"Locating first point {xkey} {ykey}")
                except Exception as e:
                    logger.warning(f"Failed to locate point: {e}")
                    sg.Popup("Error", f"Invalid coordinates {x} {y}")
            elif event == 'Extract data':
                traj = plotdigitizer.core.extract_data(img)
                logger.debug(traj)
            else:
                logger.debug(f"unhandled {event}, {values}")


if __name__ == "__main__":
    app = GUI()
    app.run()
