"""Goal identity regressions; runnable without a Home Assistant installation."""

import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "nhl_goals", Path(__file__).parents[1] / "custom_components/nhl_api/goals.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
GoalTracker = MODULE.GoalTracker


def snapshot(goal=None, game=1, state="LIVE"):
    return {"game_id": game, "goal_event_id": goal,
            "goal_team_abbrev": "MTL" if goal is not None else None,
            "game_state": state}


def test_startup_and_reload_do_not_announce_existing_goal():
    for tracker in (GoalTracker(), GoalTracker()):
        assert not tracker.is_new_goal(snapshot(10))
        assert not tracker.is_new_goal(snapshot(10))
        assert tracker.is_new_goal(snapshot(11))


def test_first_goal_after_scoreless_baseline_and_consecutive_goals():
    tracker = GoalTracker()
    assert not tracker.is_new_goal(snapshot())
    assert tracker.is_new_goal(snapshot(10))
    assert tracker.is_new_goal(snapshot(11))
    assert not tracker.is_new_goal(snapshot(10))


def test_final_does_not_reset_history_and_final_goal_is_delivered():
    tracker = GoalTracker()
    tracker.is_new_goal(snapshot(10))
    assert tracker.is_new_goal(snapshot(11, state="FINAL"))
    for _ in range(5):
        assert not tracker.is_new_goal(snapshot(11, state="FINAL"))


def test_game_identity_and_id_type_normalization():
    tracker = GoalTracker()
    tracker.is_new_goal(snapshot(10))
    assert not tracker.is_new_goal(snapshot("10", game="1"))
    assert tracker.is_new_goal(snapshot(10, game=2))
    assert not tracker.is_new_goal(snapshot(10, game=2))


def test_missing_data_does_not_erase_history():
    tracker = GoalTracker()
    assert not tracker.is_new_goal({})
    assert not tracker.is_new_goal(snapshot(10))
    assert not tracker.is_new_goal(snapshot(game=None))
    assert not tracker.is_new_goal(snapshot(10))
    assert tracker.is_new_goal(snapshot(11))


def test_no_game_startup_then_new_game_goal():
    tracker = GoalTracker()
    assert not tracker.is_new_goal(snapshot(game=None, state="No Game Scheduled"))
    assert tracker.is_new_goal(snapshot(10))
