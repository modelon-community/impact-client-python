"""Tests for the plots a view write builds.

The UI applies a stored layout verbatim and reads the plot back through its own store,
so what matters here is that a plot written by the client occupies a real grid slot it
does not share, and carries the fields the dashboard reads.

"""
from typing import Any, Dict, List, Optional
from unittest import mock

import pytest

from modelon.impact.client.entities.modeling import ModelingSession
from modelon.impact.client.exceptions import NoProjectFoundForClassError
from modelon.impact.client.views import (
    ITEM_HEIGHT_IN_ROWS,
    ITEM_WIDTH_IN_COLUMNS,
    build_plot,
    first_free_slot,
    next_plot_name,
)


def _plot_at(x: int, y: int) -> Dict[str, Any]:
    return {
        "x": x,
        "y": y,
        "width": ITEM_WIDTH_IN_COLUMNS,
        "height": ITEM_HEIGHT_IN_ROWS,
    }


class TestPlacement:
    def test_the_first_plot_takes_the_top_left_cell(self):
        assert first_free_slot([]) == (0, 0)

    def test_a_second_plot_goes_beside_the_first(self):
        assert first_free_slot([_plot_at(0, 0)]) == (ITEM_WIDTH_IN_COLUMNS, 0)

    def test_a_full_row_pushes_the_next_plot_onto_a_new_one(self):
        # Three 4-column items fill the 12-column grid.
        full_row = [_plot_at(0, 0), _plot_at(4, 0), _plot_at(8, 0)]

        assert first_free_slot(full_row) == (0, ITEM_HEIGHT_IN_ROWS)

    def test_a_gap_left_by_a_removed_plot_is_filled_before_a_new_row(self):
        assert first_free_slot([_plot_at(4, 0), _plot_at(8, 0)]) == (0, 0)

    def test_a_plot_stored_without_a_layout_does_not_claim_the_grid(self):
        # The UI writes zeros for a plot the grid has not laid out yet; treating that as
        # an occupied cell would push every later plot down a row for nothing.
        assert first_free_slot([{"x": 0, "y": 0, "width": 0, "height": 0}]) == (0, 0)


class TestPlot:
    def test_it_carries_the_variables_and_the_type_the_dashboard_reads(self):
        plot = build_plot(["resistor.v", "resistor.i"], [], plot_type="line")

        assert plot["variables"] == ["resistor.v", "resistor.i"]
        assert plot["config"]["type"] == "LINE"
        assert plot["width"] == ITEM_WIDTH_IN_COLUMNS
        assert plot["height"] == ITEM_HEIGHT_IN_ROWS

    def test_an_unnamed_axis_is_left_to_the_dashboard(self):
        # Empty, not "time": the UI reads an empty axis as "you choose" and picks the
        # right one for the result, which is not time for a steady-state sweep.
        assert build_plot(["h"], [])["independentVariable"] == ""

    def test_a_named_axis_is_kept(self):
        plot = build_plot(["h"], [], independent_variable="time")

        assert plot["independentVariable"] == "time"

    def test_each_plot_gets_an_identity_of_its_own(self):
        # The title field is the plot's id within the view, not its label.
        first = build_plot(["h"], [])
        second = build_plot(["h"], [first])

        assert first["title"] != second["title"]
        assert first["title"].startswith("analyze-dashboard-item-")

    def test_a_scatter_plot_puts_cases_on_the_x_axis(self):
        assert (
            build_plot(["h"], [], plot_type="scatter")["axes"]["x"]["type"] == "cases"
        )
        assert build_plot(["h"], [])["axes"]["x"]["type"] == "default"

    def test_an_unnamed_plot_continues_the_dashboard_numbering(self):
        existing = [build_plot(["h"], [])]

        assert next_plot_name(existing) == "Plot 2"
        assert build_plot(["v"], existing)["config"]["layout"]["title"] == {
            "text": "Plot 2"
        }

    def test_a_named_plot_keeps_its_name(self):
        plot = build_plot(["h"], [], title="Tank level")

        assert plot["config"]["layout"]["title"] == {"text": "Tank level"}


def _session(views: Optional[List[Dict[str, Any]]] = None) -> ModelingSession:
    modeling_sal = mock.MagicMock()
    modeling_sal.get_top_classes.return_value = {
        "other_project": [{"name": "LibB"}],
        "owning_project": [{"name": "LibA"}],
    }
    modeling_sal.get_views.return_value = views or []
    return ModelingSession(
        "session_id", "workspace_id", "default_project", modeling_sal, mock.MagicMock()
    )


@pytest.mark.experimental
class TestAddAnalysisPlot:
    def test_a_class_without_a_dashboard_gets_one_holding_the_plot(self):
        session = _session()

        session.add_analysis_plot("LibA.Tank", ["tank.level"])

        definition = session._modeling_sal.create_view.call_args.args[2]
        assert definition["kind"] == "ANALYSIS"
        assert [plot["variables"] for plot in definition["plots"]] == [["tank.level"]]

    def test_a_second_plot_is_added_beside_the_one_already_there(self):
        existing = build_plot(["tank.level"], [])
        session = _session([{"metadata": {"viewId": "view_id"}, "plots": [existing]}])

        session.add_analysis_plot("LibA.Tank", ["tank.inflow"])

        _, _, view_id, definition = session._modeling_sal.update_view.call_args.args
        assert view_id == "view_id"
        assert [plot["variables"] for plot in definition["plots"]] == [
            ["tank.level"],
            ["tank.inflow"],
        ]
        assert definition["plots"][1]["x"] == ITEM_WIDTH_IN_COLUMNS

    def test_the_settings_the_user_chose_for_the_dashboard_survive_the_write(self):
        # globalConfig holds the reference experiment and colour mode; rebuilding the
        # definition without it would silently reset both.
        global_config = {"referenceExperimentId": "experiment_id"}
        session = _session(
            [
                {
                    "metadata": {"viewId": "view_id"},
                    "plots": [],
                    "globalConfig": global_config,
                }
            ]
        )

        session.add_analysis_plot("LibA.Tank", ["tank.level"])

        definition = session._modeling_sal.update_view.call_args.args[3]
        assert definition["globalConfig"] == global_config

    def test_the_plot_goes_to_the_project_that_owns_the_class(self):
        # Not the session's default project: a view is stored per project, so writing
        # to the wrong one puts the plot on a dashboard nobody opens.
        session = _session()

        session.add_analysis_plot("LibA.Tank", ["tank.level"])

        assert session._modeling_sal.create_view.call_args.args[0] == "owning_project"

    def test_a_class_no_project_holds_is_reported_as_such(self):
        session = _session()

        with pytest.raises(NoProjectFoundForClassError):
            session.add_analysis_plot("LibC.Tank", ["tank.level"])

    def test_the_plot_is_described_the_way_it_was_asked_for(self):
        session = _session()

        plot = session.add_analysis_plot(
            "LibA.Tank", ["tank.level"], plot_type="scatter", title="Tank level"
        )

        assert plot.title == "Tank level"
        assert plot.variables == ["tank.level"]
        assert plot.plot_type == "scatter"
        # None rather than "", so the caller can tell "the dashboard decides" from an
        # axis that was actually named.
        assert plot.independent_variable is None

    def test_a_plot_type_the_dashboard_cannot_draw_is_refused_before_writing(self):
        session = _session()

        with pytest.raises(ValueError):
            session.add_analysis_plot("LibA.Tank", ["tank.level"], plot_type="pie")
        session._modeling_sal.create_view.assert_not_called()

    def test_a_plot_with_no_variables_is_refused_before_writing(self):
        session = _session()

        with pytest.raises(ValueError):
            session.add_analysis_plot("LibA.Tank", [])
        session._modeling_sal.create_view.assert_not_called()
