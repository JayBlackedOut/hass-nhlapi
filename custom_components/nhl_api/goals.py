"""Track goal identity independently of polling and entity state."""


class GoalTracker:
    """Deduplicate goals within a game and suppress the startup snapshot."""

    def __init__(self) -> None:
        self._initialized = False
        self._game_id: str | None = None
        self._seen: set[tuple[str, str]] = set()

    def is_new_goal(self, attributes: dict) -> bool:
        """Return whether a successful snapshot contains a new goal."""
        if not attributes:
            return False
        baseline = not self._initialized
        self._initialized = True
        game_id = attributes.get("game_id")
        if game_id is None:
            return False
        game_id = str(game_id)
        if game_id != self._game_id:
            self._game_id = game_id
            self._seen.clear()
        event_id = attributes.get("goal_event_id")
        if event_id is None or not attributes.get("goal_team_abbrev"):
            return False
        key = (game_id, str(event_id))
        if key in self._seen:
            return False
        self._seen.add(key)
        return not baseline
