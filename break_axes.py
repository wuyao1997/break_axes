"""
A Matplotlib-based utility module for creating broken axes and custom axis scaling.

This module provides a comprehensive set of functions to handle axis breaks (visual gaps)
and flexible axis scaling, addressing limitations of Matplotlib's native axis handling.
It enables clear visualization of data with large spans or irrelevant intervals by:
- Drawing broken line markers to indicate axis breaks
- Generating clipping paths to hide unwanted axis segments and plot elements
- Supporting custom linear/logarithmic scaling across multiple data intervals

Key Features:
- Add break markers on axis edges (lower/upper/both)
- Clip spines and plot elements to match break positions
- Create multi-interval axis scaling with custom scale factors
- Ensure consistent visual offsets regardless of axis scaling

Main Functions:
- `broken_and_clip_axes`: One-stop function to add break markers and apply clipping
- `scale_axes`: Configure custom scaling for x/y axes
- `add_broken_line_in_axis`: Draw break markers on specific axis edges
- `clip_axes`: Apply clipping to spines and plot elements around breaks

Dependencies:
- matplotlib (for axes, lines, paths, transforms)
- typing (for type hints)

Version: 0.1.0
Author: Wu Yao <wuyao1997@qq.com>
"""

__all__ = ["broken_and_clip_axes", "scale_axes"]

from typing import Literal

from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.path import Path
from matplotlib.scale import FuncScale, FuncScaleLog
from matplotlib.spines import Spine
from matplotlib.text import Text
import matplotlib.transforms as mtransforms


__version__ = "0.1.0"
__author__ = "Wu Yao <wuyao1997@qq.com>"


def create_scale(
    interval: list[tuple[float, float, float]],
    mode: Literal["linear", "log"] = "linear",
) -> FuncScale | FuncScaleLog:
    """Create a ScaleBase object by FuncScale or FuncScaleLog.

    Parameters
    ----------
    interval : list[Tuple[float, float, float]]
        [(a1, b1, f1), (a2, b2, f2), ...], where a1 < b1 < a2 < b2 < ...,
        f1 > 0, f2 > 0, ..., and f1, f2 are the scale factor of [a1, b1] and [a2, b2]...
    mode : Literal["linear", "log"], optional
        Scale mode, by default "linear"

    Returns
    -------
    FuncScale | FuncScaleLog
        ScaleBase object which could be passed to ax.set_xscale() or ax.set_yscale()

    Raises
    ------
    ValueError
        Input interval must be non-overlapping and sorted.
    ValueError
        Input scale factor must be positive.
    """
    x0, factor = [], []
    _prev_b = float("-inf")
    # It can be improved. Floating-point numbers are not suitable for direct comparison.
    for a, b, f in interval:
        if not ((a < b) and (_prev_b <= a)):
            raise ValueError("Input interval must be non-overlapping and sorted.")
        if f <= 0:
            raise ValueError("c must be positive")
        x0.extend([a, b]) if _prev_b < a else x0.extend([b])
        if _prev_b < a:
            factor.extend([f, 1])
        else:
            factor.insert(-1, f)
        _prev_b = b

    N = len(x0)

    def _forward(x):
        res = x.copy()

        ymin = x0[0]
        for n in range(N - 1):
            xmin, xmax = x0[n], x0[n + 1]
            cond = (x > xmin) & (x <= xmax)
            res[cond] = (x[cond] - xmin) * factor[n] + ymin
            ymin += (xmax - xmin) * factor[n]

        res[x > xmax] = (x[x > xmax] - xmax) * factor[-1] + ymin

        return res

    def _inverse(y):
        res = y.copy()

        ymin = x0[0]
        for n in range(N - 1):
            xmin, xmax = x0[n], x0[n + 1]
            ymax = ymin + (xmax - xmin) * factor[n]
            cond = (y > ymin) & (y <= ymax)
            res[cond] = (y[cond] - ymin) / factor[n] + xmin

            ymin = ymax

        res[y > ymax] = (y[y > ymax] - ymax) / factor[-1] + xmax

        return res

    if mode == "linear":
        return FuncScale(None, functions=(_forward, _inverse))
    else:
        return FuncScaleLog(None, functions=(_forward, _inverse))


def scale_axis(
    ax: Axes,
    interval: list[tuple[float, float, float]],
    axis: Literal["x", "y"] = "x",
    mode: Literal["linear", "log"] = "linear",
) -> None:
    """Scale the axis by the given interval and factor.

    Parameters
    ----------
    ax : Axes
        The axes to scale.
    interval : list[Tuple[float, float, float]]
        [(a1, b1, f1), (a2, b2, f2), ...], where a1 < b1 < a2 < b2 < ...,
        f1 > 0, f2 > 0, ..., and f1, f2 are the scale factor of [a1, b1] and [a2, b2]...
    axis : Literal["x", "y"], optional
        The axis to scale, by default "x"
    mode : Literal["linear", "log"], optional
        Scale mode, by default "linear"
    """
    if axis not in ["x", "y"]:
        raise ValueError("axis must be 'x' or 'y'")
    scale = create_scale(interval, mode=mode)
    if axis == "x":
        ax.set_xscale(scale)
    if axis == "y":
        ax.set_yscale(scale)
    return


def offset_data_point(
    ax: Axes, x: float, y: float, dx_pt: float = 0, dy_pt: float = 0
) -> tuple[float, float]:
    """
    Offset a data point by specified amounts in points and return new coordinates.

    Converts the original data coordinates to display coordinates, applies the
    specified offset in points (converted to inches), then converts back to
    data coordinates for the final result.

    Parameters
    ----------
    ax : Axes
        Matplotlib Axes object containing the data point
    x : float
        Original x-coordinate in data space
    y : float
        Original y-coordinate in data space
    dx_pt : float, optional
        Horizontal offset in points (1 point = 1/72 inch), by default 0
    dy_pt : float, optional
        Vertical offset in points (1 point = 1/72 inch), by default 0

    Returns
    -------
    tuple[float, float]
        New (x, y) coordinates in data space after applying the offset

    Notes
    -----
    This function preserves consistent visual offsets regardless of axis scaling,
    which is useful for annotating plots with fixed positional offsets.
    """
    # Convert data coordinates to display coordinates (pixels)
    x, y = float(x), float(y)
    x_disp, y_disp = ax.transData.transform((x, y))

    # Create physical offset conversion (points to inches)
    dx_inch = dx_pt / 72
    dy_inch = dy_pt / 72
    offset = mtransforms.ScaledTranslation(dx_inch, dy_inch, ax.figure.dpi_scale_trans)
    x_off, y_off = offset.transform((x_disp, y_disp))

    # Convert back from display coordinates to data coordinates
    x_new, y_new = ax.transData.inverted().transform((x_off, y_off))

    return x_new, y_new


def get_broken_points(
    ax: Axes, x: float, y: float, axis: str, gap: float, dx: float, dy: float
) -> list[tuple[float, float]]:
    """
    Calculate coordinates for a broken line marker  at a given data point.
                    P1       P3                            |
                    /       /                              | /P3
    ---------------/       /-----------------              |/
                  /       /                                /
                P0       P2                               /  /P1
                                                       P2/  /
                                                           /
                                                          /|
                                                         / |
                                                       P0  |

    Generates four points that form a broken line marker, typically used to indicate a
    break in an axis or data line. The marker's orientation depends on the specified
    axis ('x' or 'y').

    The marker is defined by four points:
    1. (x, y) - Center point
    2. (x + dx, y + dy) - Top-right point
    3. (x - dx, y - dy) - Bottom-left point
    4. (x + dx, y - dy) - Bottom-right point

    Parameters
    ----------
    ax : Axes
        Matplotlib Axes object containing the data point
    x : float
        x-coordinate of the center point in data space
    y : float
        y-coordinate of the center point in data space
    axis : str
        Axis orientation for the break marker, must be either 'x' or 'y'
    gap : float
        Total length of the gap in points (1 point = 1/72 inch)
    dx : float
        Horizontal offset component for the marker lines in points
    dy : float
        Vertical offset component for the marker lines in points

    Returns
    -------
    list[tuple[float, float]]
        List of four (x, y) coordinate tuples in data space representing the vertices of
        the broken line marker, ordered to form the break symbol when connected
        sequentially

    Raises
    ------
    ValueError
        If `axis` is not 'x' or 'y'
    """
    if axis not in ["x", "y"]:
        raise ValueError("which must be 'x' or 'y'")
    if axis == "x":
        gap_x, gap_y = gap / 2.0, 0
    else:
        gap_x, gap_y = 0, gap / 2.0

    x0, y0 = offset_data_point(ax, x, y, -gap_x - dx, -gap_y - dy)
    x1, y1 = offset_data_point(ax, x, y, -gap_x + dx, -gap_y + dy)
    x2, y2 = offset_data_point(ax, x, y, gap_x - dx, gap_y - dy)
    x3, y3 = offset_data_point(ax, x, y, gap_x + dx, gap_y + dy)
    return [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]


def xy2points(
    x: float | list[float], y: float | list[float]
) -> list[tuple[float, float]]:
    """
    Convert x and y values into a list of (x, y) coordinate tuples.

    Handles various combinations of scalar and list inputs for x and y,
    returning a consistent list of coordinate tuples.

    Parameters
    ----------
    x : float | list[float]
        Scalar x-value or list of x-values
    y : float | list[float]
        Scalar y-value or list of y-values

    Returns
    -------
    list[tuple[float, float]]
        List of (x, y) coordinate tuples derived from input values

    Raises
    ------
    AssertionError
        - If both x and y are lists but have different lengths
        - If a list input contains non-numeric elements
    ValueError
        If inputs are not combinations of scalars (float/int) or lists of scalars

    Examples
    --------
    >>> xy2points(1.5, 3.0)
    [(1.5, 3.0)]

    >>> xy2points([1, 2, 3], 5)
    [(1, 5), (2, 5), (3, 5)]

    >>> xy2points(4, [6, 7, 8])
    [(4, 6), (4, 7), (4, 8)]

    >>> xy2points([1, 2], [3, 4])
    [(1, 3), (2, 4)]
    """
    if isinstance(x, list) and isinstance(y, list):
        assert len(x) == len(y), (
            "if both x and y are list, they must have the same length"
        )
    if isinstance(x, (float, int)) and isinstance(y, (float, int)):
        return [(x, y)]
    if isinstance(x, list) and isinstance(y, (float, int)):
        assert all(isinstance(px, (int, float)) for px in x), (
            "if x is list, all elements must be float or int"
        )
        return [(x, y) for x in x]
    if isinstance(x, (float, int)) and isinstance(y, list):
        assert all(isinstance(py, (int, float)) for py in y), (
            "if y is list, all elements must be float or int"
        )
        return [(x, y) for y in y]

    raise ValueError("x and y must be list[float|int] or float")


def add_broken_line(
    ax: Axes,
    x: float | list[float],
    y: float | list[float],
    axis: Literal["x", "y"] = "x",
    gap: float = 5,
    dx: float = 3,
    dy: float = 3,
    **kwargs,
) -> list[tuple[Line2D, Line2D]]:
    """
    Add broken line markers to a matplotlib Axes at specified coordinates.

    Creates and draws broken line markers (typically used to indicate axis breaks)
    at given (x, y) positions. The markers can be oriented horizontally ('x') or
    vertically ('y') and are customizable in appearance.

    Parameters
    ----------
    ax : Axes
        Matplotlib Axes object where the broken lines will be added
    x : float | list[float]
        Scalar x-coordinate or list of x-coordinates for marker positions
    y : float | list[float]
        Scalar y-coordinate or list of y-coordinates for marker positions
    axis : Literal["x", "y"], optional
        Orientation of the broken lines, 'x' (default) or 'y'
    gap : float, optional
        Total length of the gap in points (1 point = 1/72 inch), default is 5
    dx : float, optional
        Horizontal offset component for marker lines in points, default is 3
    dy : float, optional
        Vertical offset component for marker lines in points, default is 3
    **kwargs
        Additional keyword arguments passed to matplotlib's plot() function
        (e.g., color, linestyle, linewidth). Defaults include:
        - color: 'black'
        - lw: 1.5
        - clip_on: False

    Returns
    -------
    list[tuple[Line2D, Line2D]]
        List of tuples, each containing two Line2D objects representing the
        two segments of each broken line marker

    Raises
    ------
    ValueError
        If `axis` is not 'x' or 'y'
    AssertionError
        From xy2points() if input coordinate combinations are invalid

    Examples
    --------
    Add a horizontal horizontal broken line at (5, 10):
    >>> add_broken_line(ax, 5, 10)

    Add vertical broken lines at multiple y-positions along x=3:
    >>> add_broken_line(ax, 3, [2, 4, 6], axis='y', color='red')
    """
    if axis not in ["x", "y"]:
        raise ValueError("which must be 'x' or 'y'")
    points = xy2points(x, y)

    if "color" not in kwargs:
        kwargs["color"] = "black"
    if "lw" not in kwargs:
        kwargs["lw"] = 1.5
    if "clip_on" not in kwargs:
        kwargs["clip_on"] = False

    results = []
    for x, y in points:
        points = get_broken_points(ax, x, y, axis, gap, dx, dy)
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        l1, l2 = ax.plot(x[:2], y[:2], x[2:], y[2:], **kwargs)
        results.append((l1, l2))

    return results


def get_axis_clip_path(
    ax: Axes,
    x: float | list[float],
    y: float | list[float],
    axis="x",
    gap: float = 5,
    dx: float = 3,
    dy: float = 3,
    extend: float = None,
) -> Path:
    """
    Generate a clipping path for axis breaks with extendable boundary offsets.

    Creates a matplotlib Path object defining a clipping region to hide axis segments
    between break markers. The path incorporates an extend parameter to control boundary
    offsets, preventing clipping artifacts at spine ends.

    Parameters
    ----------
    ax : Axes
        Matplotlib Axes object for which the clipping path is created
    x : float | list[float]
        Scalar x-coordinate or list of x-coordinates where axis breaks are located
    y : float | list[float]
        Scalar y-coordinate or list of y-coordinates where axis breaks are located
    axis : str, optional
        Axis for clipping path orientation, 'x' (default) or 'y'
    gap : float, optional
        Total length of the break gap in points (1 point = 1/72 inch), default is 5
    dx : float, optional
        Horizontal offset component for break markers in points, default is 3
    dy : float, optional
        Vertical offset component for break markers in points, default is 3
    extend : float, optional
        Extension distance in points for boundary offsets.
        If None (default), uses `gap` value. This extension ensures the clipping region
        extends to the ends of spines and ticklines, preventing incomplete coverage.

    Returns
    -------
    Path
        Matplotlib Path object

    """

    extend = gap if extend is None else extend
    dx += extend
    dy += extend

    if axis == "x":
        xlow, xhigh = ax.get_xlim()
        ylow = y[0] if isinstance(y, list) else y
        yhigh = y[-1] if isinstance(y, list) else y
        x0, y0 = offset_data_point(ax, xlow, ylow, -extend - dx, -dy)
        x1, y1 = offset_data_point(ax, xlow, ylow, -extend + dx, dy)
        x2, y2 = offset_data_point(ax, xhigh, yhigh, extend - dx, -dy)
        x3, y3 = offset_data_point(ax, xhigh, yhigh, extend + dx, dy)
    else:
        ylow, yhigh = ax.get_ylim()
        xlow = x[0] if isinstance(x, list) else x
        xhigh = x[-1] if isinstance(x, list) else x
        x0, y0 = offset_data_point(ax, xlow, ylow, -dx, -extend - dy)
        x1, y1 = offset_data_point(ax, xlow, ylow, dx, -extend + dy)
        x2, y2 = offset_data_point(ax, xhigh, yhigh, -dx, extend - dy)
        x3, y3 = offset_data_point(ax, xhigh, yhigh, dx, extend + dy)

    points_lst = [(x0, y0), (x1, y1)]
    for x, y in xy2points(x, y):
        points = get_broken_points(ax, x, y, axis, gap, dx, dy)
        points_lst.extend(points)
    points_lst.extend([(x2, y2), (x3, y3)])

    N = int(len(points_lst) / 4)
    vertices, codes = [], []
    for i in range(N):
        points = points_lst[i * 4 : i * 4 + 4]
        vertices.extend([points[0], points[1], points[3], points[2], points[0]])
        codes.extend([Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY])

    path = Path(vertices, codes)
    return path


def get_axes_clip_path(
    ax: Axes, x: float | list[float], y: float | list[float], gap: float = 5.0
) -> Path:
    """
    Generate a clipping path for matplotlib Axes to exclude regions around specified
    break points.

    Creates a matplotlib Path object that defines a clipping region, typically used to
    hide parts of the Axes (e.g., plot lines or bars) around user-specified x and y
    break positions. The path is constructed by dividing the axis ranges into segments
    separated by gaps at the break points.

    Parameters
    ----------
    ax : Axes
        Matplotlib Axes object for which the clipping path is generated
    x : float | list[float]
        Scalar x-coordinate or list of x-coordinates where horizontal breaks are placed
    y : float | list[float]
        Scalar y-coordinate or list of y-coordinates where vertical breaks are placed
    gap : float, optional
        Gap width, default is 5.0

    Returns
    -------
    Path
        Matplotlib Path object defining the clipping region.
        This region consists of closed rectangular segments that cover the Axes area
        excluding the gaps around the specified x and y break points.
    """
    xlow, xhigh = ax.get_xlim()
    xlst = [xlow]
    for _x in x:
        x0, _ = offset_data_point(ax, _x, 0, -gap / 2.0)
        x1, _ = offset_data_point(ax, _x, 0, gap / 2.0)
        xlst.extend([x0, x1])
    xlst.append(xhigh)

    ylow, yhigh = ax.get_ylim()
    ylst = [ylow]
    for _y in y:
        _, y0 = offset_data_point(ax, 0, _y, 0, -gap / 2.0)
        _, y1 = offset_data_point(ax, 0, _y, 0, gap / 2.0)
        ylst.extend([y0, y1])
    ylst.append(yhigh)

    xlst = [xlst[i : i + 2] for i in range(0, len(xlst), 2)]
    ylst = [ylst[i : i + 2] for i in range(0, len(ylst), 2)]

    vertices, codes = [], []
    for x in xlst:
        for y in ylst:
            x0, x1 = x[0], x[1]
            y0, y1 = y[0], y[1]

            p0 = (x0, y0)
            p1 = (x1, y0)
            p2 = (x1, y1)
            p3 = (x0, y1)
            vertices.extend([p0, p1, p2, p3, p0])
            codes.extend([Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY])

    return Path(vertices, codes)


def scale_axes(
    ax: Axes,
    x_interval: list[tuple[float, float, float]],
    y_interval: list[tuple[float, float, float]],
    mode: Literal["linear", "log"] = "linear",
) -> None:
    """
    Configure scale and visible intervals for Axes x/y axes.

    Wraps `scale_axis` to set linear/log scale and visible data intervals for x-axis,
    y-axis, or both.

    Parameters
    ----------
    ax : Axes
        Matplotlib Axes to configure
    x_interval : list[tuple[float, float, float]]
        X-axis intervals: each tuple is (start, end, scale_factor); empty to no change
    y_interval : list[tuple[float, float, float]]
        Y-axis intervals: same format as x_interval; empty to no change
    mode : Literal["linear", "log"], optional
        Scale type for axes, default "linear"

    Returns
    -------
    None
        Modifies Axes in-place
    """
    if x_interval:
        scale_axis(ax, x_interval, axis="x", mode=mode)
    if y_interval:
        scale_axis(ax, y_interval, axis="y", mode=mode)
    return


def add_broken_line_in_axis(
    ax: Axes,
    x: list[float] | float = None,
    y: list[float] | float = None,
    which: Literal["lower", "upper", "both"] = "both",
    gap: float = 5,
    dx: float = 3,
    dy: float = 3,
    **line_kwargs,
) -> dict[str, list[tuple[Line2D, Line2D]]]:
    """
    Add broken lines to Axes edges (x/y axis bounds) at specified positions.

    Wraps `add_broken_line` to draw break markers on axis lower/upper edges
    (xlim/ylim bounds).

    Parameters
    ----------
    ax : Axes
        Matplotlib Axes to add broken lines
    x : list[float] | float, optional
        X positions for x-axis edge breaks; None = no x-axis breaks
    y : list[float] | float, optional
        Y positions for y-axis edge breaks; None = no y-axis breaks
    which : Literal["lower", "upper", "both"], optional
        Edge(s) to add breaks: "lower" (axis min), "upper" (axis max), or "both",
        default "both"
    gap : float, optional
        Break gap size in points, default 5
    dx : float, optional
        Horizontal offset for break lines in points, default 3
    dy : float, optional
        Vertical offset for break lines in points, default 3
    **line_kwargs
        Additional args passed to `add_broken_line` (e.g., color, lw)

    Returns
    -------
    list[tuple[Line2D, Line2D]]
        List of Line2D tuples for all added broken lines


    Note
    ----
    Please fix the axis display range via ax.set(xlim=..., ylim=...) or ax.set_xlim(...)
    and ax.set_ylim(...) before calling this function.
    """
    if which not in ["lower", "upper", "both"]:
        raise ValueError("which must be 'lower', 'upper' or 'both'")

    kwargs = dict(gap=gap, dx=dx, dy=dy, **line_kwargs)

    broken_lines = {}
    if x:
        ylow, yhigh = ax.get_ylim()
        if which in ["lower", "both"]:
            broken_line = add_broken_line(ax, x, ylow, axis="x", **kwargs)
            broken_lines["bottom"] = broken_line
        if which in ["upper", "both"]:
            broken_line = add_broken_line(ax, x, yhigh, axis="x", **kwargs)
            broken_lines["top"] = broken_line

    if y:
        xlow, xhigh = ax.get_xlim()
        if which in ["lower", "both"]:
            broken_line = add_broken_line(ax, xlow, y, axis="y", **kwargs)
            broken_lines["left"] = broken_line
        if which in ["upper", "both"]:
            broken_line = add_broken_line(ax, xhigh, y, axis="y", **kwargs)
            broken_lines["right"] = broken_line
    return broken_lines


def clip_axes(
    ax: Axes,
    x: list[float] | float = None,
    y: list[float] | float = None,
    which: Literal["lower", "upper", "both"] = "both",
    axes_clip: bool = True,
    gap: float = 5,
    dx: float = 3,
    dy: float = 3,
    extend: float = None,
):
    """
    Apply clipping to Axes spines and elements at specified break positions.

    Clips artists in axes (excluding text/spines) based on break positions,
    hiding parts between breaks using generated clip paths.

    Parameters
    ----------
    ax : Axes
        Matplotlib Axes to apply clipping
    x : list[float] | float, optional
        X positions for x-axis clipping; None = no x-clipping
    y : list[float] | float, optional
        Y positions for y-axis clipping; None = no y-clipping
    which : Literal["lower", "upper", "both"], optional
        Spines to clip: "lower", "upper", or "both", default "both"
    axes_clip : bool, optional
        Whether to clip non-spine elements, default True
    gap : float, optional
        Break gap size in points, default 5
    dx : float, optional
        Horizontal offset for clip paths, default 3
    dy : float, optional
        Vertical offset for clip paths, default 3
    extend : float, optional
        Extension for clip paths; uses `gap` if None, default None

    Returns
    -------
    None
        Modifies Axes in-place

    Note
    ----
    Please fix the axis display range via ax.set(xlim=..., ylim=...) or ax.set_xlim(...)
    and ax.set_ylim(...) before calling this function.
    """
    if which not in ["lower", "upper", "both"]:
        raise ValueError("which must be 'lower', 'upper' or 'both'")

    extend = gap if extend is None else extend
    kwargs = dict(gap=gap, dx=dx, dy=dy, extend=extend)

    if x:
        ylow, yhigh = ax.get_ylim()
        if which in ["lower", "both"]:
            clip_path = get_axis_clip_path(ax, x, ylow, axis="x", **kwargs)
            ax.spines["bottom"].set_clip_path(clip_path, transform=ax.transData)
        if which in ["high", "both"]:
            clip_path = get_axis_clip_path(ax, x, yhigh, axis="x", **kwargs)
            ax.spines["top"].set_clip_path(clip_path, transform=ax.transData)

    if y:
        xlow, xhigh = ax.get_xlim()
        if which in ["lower", "both"]:
            clip_path = get_axis_clip_path(ax, xlow, y, axis="y", **kwargs)
            ax.spines["left"].set_clip_path(clip_path, transform=ax.transData)
        if which in ["high", "both"]:
            clip_path = get_axis_clip_path(ax, xhigh, y, axis="y", **kwargs)
            ax.spines["right"].set_clip_path(clip_path, transform=ax.transData)

    if axes_clip:
        axes_clip_path = get_axes_clip_path(ax, x, y, gap)

        for art in ax.get_children():
            if isinstance(art, (Text, Spine)):
                continue
            if id(art) == id(ax.patch):
                continue
            art.set_clip_path(axes_clip_path, ax.transData)
    return


def broken_and_clip_axes(
    ax: Axes,
    x: list[float] | float = None,
    y: list[float] | float = None,
    axes_clip: bool = True,
    which: Literal["lower", "upper", "both"] = "both",
    gap: float = 5,
    dx: float = 3,
    dy: float = 3,
    extend: float = None,
    **kwargs,
) -> dict[str, list[tuple[Line2D, Line2D]]]:
    """
    Wrapper to add broken line markers AND apply axis clipping in one call.

    Combines the functionality of `add_broken_line_in_axis` (draws break markers)
    and `clip_axes` (hides axis/spine parts between breaks).

    Parameters
    ----------
    ax : Axes
        Matplotlib Axes object to add breaks and apply clipping
    x : list[float] | float, optional
        X-axis positions where breaks are placed
        (passed to `add_broken_line_in_axis` and `clip_axes`).
        None = no breaks/clipping on x-axis
    y : list[float] | float, optional
        Y-axis positions where breaks are placed
        (passed to `add_broken_line_in_axis` and `clip_axes`).
        None = no breaks/clipping on y-axis
    axes_clip : bool, optional
        Whether to clip non-spine Axes elements (e.g., lines, markers) between breaks
        (passed to `clip_axes`).
        True = clip elements; False = only clip spines
    which : Literal["lower", "upper", "both"], optional
        Which axis edges to apply breaks/clipping to (passed to both wrapped functions):
        - "lower": Lower edge (x-axis bottom, y-axis left)
        - "upper": Upper edge (x-axis top, y-axis right)
        - "both": Both lower and upper edges
    gap : float, optional
        Total size of the break gap (in points, 1pt=1/72 inch)
        (passed to both wrapped functions).
        Controls spacing of broken line markers and clip path gaps
    dx : float, optional
        Horizontal offset for broken line markers (passed to both wrapped functions).
        Adjusts the "angle" of break marker lines
    dy : float, optional
        Vertical offset for broken line markers (passed to both wrapped functions).
        Adjusts the "angle" of break marker lines
    extend : float, optional
        Extension distance (in points) for clip paths (passed to `clip_axes`).
        Ensures clip paths cover spine/tickline ends; uses `gap` value if None
    **kwargs
        Additional keyword arguments for broken line styling
        (passed to `add_broken_line_in_axis`).
        E.g., `color='red'`, `lw=2` to customize break marker appearance

    Returns
    -------
    None
        Modifies the Axes object in-place (adds markers + applies clipping)

    Note
    ----
    Please fix the axis display range via ax.set(xlim=..., ylim=...) or ax.set_xlim(...)
    and ax.set_ylim(...) before calling this function.
    """
    broken_lines = add_broken_line_in_axis(ax, x, y, which, gap, dx, dy, **kwargs)
    clip_axes(ax, x, y, which, axes_clip, gap, dx, dy, extend)
    return broken_lines
