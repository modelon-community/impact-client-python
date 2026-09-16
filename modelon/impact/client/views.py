"""Building the plots stored in a class's analysis dashboard.

The analysis dashboard is a view the modeling server stores, one per class per project,
and the UI reads it into its own store. Everything here builds the same payload the UI
writes for a plot the user dragged in, because a plot that reaches the view by another
shape renders differently from one the user made.

"""
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

ANALYSIS_KIND = "ANALYSIS"

# The dashboard's grid, mirrored from ui-core's responsive-grid constants. The UI
# applies a stored layout verbatim and only auto-places an item that has none, so a
# plot written without a real slot renders as a zero-sized box.
COLUMN_COUNT = 12
ITEM_WIDTH_IN_COLUMNS = 4
ITEM_HEIGHT_IN_ROWS = 2

# The UI names a dashboard item this way, and stores that id as the plot's title. The
# title is the plot's identity within the view, not a label; what the user reads is
# the title stored on its layout.
ITEM_ID_PREFIX = "analyze-dashboard-item-"

PLOT_TYPES = {"line": "LINE", "scatter": "SCATTER", "histogram": "HISTOGRAM"}

_PLOT_TYPE_NAMES = {wire: name for name, wire in PLOT_TYPES.items()}


@dataclass
class AnalysisPlot:
    """A plot on a class's analysis dashboard.

    Attributes:
        title: The plot's heading, as the user reads it.
        variables: The result variables drawn on it.
        independent_variable: What is on the x axis, or None when the dashboard picks
            the default axis for the result being drawn.
        plot_type: One of the keys of ``PLOT_TYPES``.

    """

    title: str
    variables: List[str]
    independent_variable: Optional[str]
    plot_type: str


def _occupies(plot: Dict[str, Any]) -> Tuple[int, int, int, int]:
    return (
        int(plot.get("x") or 0),
        int(plot.get("y") or 0),
        int(plot.get("width") or 0),
        int(plot.get("height") or 0),
    )


def first_free_slot(plots: Sequence[Dict[str, Any]]) -> Tuple[int, int]:
    """Returns the grid cell a new plot goes in.

    A port of ``getFirstFreeSlot`` in ui-core, so a plot written here lands where the
    dashboard would have put it: the first cell, scanning rows then columns, with room
    for a whole item and without overlapping one already there.

    """
    occupied = [_occupies(plot) for plot in plots]
    height = max((y + h for _, y, _, h in occupied), default=0)
    grid = [[False] * COLUMN_COUNT for _ in range(height)]
    for x, y, w, h in occupied:
        for row in range(y, min(y + h, height)):
            for column in range(x, min(x + w, COLUMN_COUNT)):
                grid[row][column] = True

    for y in range(height):
        for x in range(COLUMN_COUNT):
            if _slot_is_free(grid, x, y):
                return x, y
    return 0, height


def _slot_is_free(grid: List[List[bool]], slot_x: int, slot_y: int) -> bool:
    for y in range(slot_y, slot_y + ITEM_HEIGHT_IN_ROWS):
        if y > len(grid) - 1:
            return True  # everything below the grid is free
        for x in range(slot_x, slot_x + ITEM_WIDTH_IN_COLUMNS):
            if x > COLUMN_COUNT - 1 or grid[y][x]:
                return False
    return True


def next_plot_name(plots: Iterable[Dict[str, Any]]) -> str:
    """Returns the ``Plot N`` the dashboard would name the next plot."""
    highest = 0
    for plot in plots:
        text = ((plot.get("config") or {}).get("layout") or {}).get("title")
        if isinstance(text, dict):
            text = text.get("text")
        if isinstance(text, str) and text.startswith("Plot "):
            number = text[len("Plot ") :]
            if number.isdigit():
                highest = max(highest, int(number))
    return f"Plot {highest + 1}"


def build_plot(
    variables: Sequence[str],
    existing_plots: Sequence[Dict[str, Any]],
    independent_variable: Optional[str] = None,
    plot_type: str = "line",
    title: Optional[str] = None,
) -> Dict[str, Any]:
    """Builds one dashboard plot in the shape the view stores.

    ``independentVariable`` is left empty when the caller names none. That is not a
    missing value: the UI reads an empty one as "the dashboard decides" and picks the
    default axis for the result being drawn, which is time for a dynamic result and a
    swept parameter for a steady-state one. Naming an axis here would get that wrong.

    """
    wire_type = PLOT_TYPES[plot_type]
    x, y = first_free_slot(existing_plots)
    return {
        "title": f"{ITEM_ID_PREFIX}{uuid.uuid4()}",
        "variables": list(variables),
        "independentVariable": independent_variable or "",
        "x": x,
        "y": y,
        "width": ITEM_WIDTH_IN_COLUMNS,
        "height": ITEM_HEIGHT_IN_ROWS,
        "config": {
            "common": {},
            "layout": {"title": {"text": title or next_plot_name(existing_plots)}},
            "variables": {},
            "type": wire_type,
        },
        # The dashboard puts a scatter plot's cases on the x axis; every other type
        # takes the default.
        "axes": {"x": {"type": "cases" if wire_type == "SCATTER" else "default"}},
    }


def to_analysis_plot(plot: Dict[str, Any]) -> AnalysisPlot:
    """Describes a stored plot as the caller named it, not as the view spells it."""
    config = plot.get("config") or {}
    title = ((config.get("layout") or {}).get("title") or {}).get("text", "")
    return AnalysisPlot(
        title=title,
        variables=list(plot.get("variables") or []),
        independent_variable=plot.get("independentVariable") or None,
        plot_type=_PLOT_TYPE_NAMES[config["type"]],
    )


def new_analysis_view_definition(plots: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Builds the definition that creates a class's analysis dashboard."""
    return {
        # The dashboard has a fixed file name and ignores the name it is sent; only a
        # diagram view needs one.
        "name": "",
        "kind": ANALYSIS_KIND,
        "stickies": [],
        "stickyPositions": [],
        "plots": list(plots),
    }


def updated_analysis_view_definition(
    view: Dict[str, Any], plots: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    """Builds the definition that writes ``plots`` back to an existing dashboard."""
    definition = {
        "stickies": view.get("stickies") or [],
        "stickyPositions": view.get("stickyPositions") or [],
        "plots": list(plots),
    }
    # Carried rather than rebuilt: it holds the reference experiment and the color mode
    # the user chose, which this write has no opinion about.
    if view.get("globalConfig") is not None:
        definition["globalConfig"] = view["globalConfig"]
    return definition
