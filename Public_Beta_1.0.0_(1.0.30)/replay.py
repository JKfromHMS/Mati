"""Rebuild a grid and its markings from a saved match's action history."""

from typing import Any, TypeAlias

_Action: TypeAlias = dict[str, Any]
_GridMatrix: TypeAlias = list[list[bool]]


def _derive_new_state(action: _Action) -> tuple[bool, bool]:
    """Determine a cell's new ``(selected, dimmed)`` state from one action.

    Newer save files store both states explicitly; older ones only store the
    previous selection and derive the new state by toggling it.
    """
    if "new_sel" in action and "new_dimmed" in action:
        return bool(action["new_sel"]), bool(action["new_dimmed"])

    action_type = action.get("type")
    prev_sel = bool(action.get("prev_sel", False))
    prev_dimmed = bool(action.get("prev_dimmed", False))

    if action_type == "Left":
        return not prev_sel, False
    if action_type == "Right":
        return False, not prev_dimmed

    return prev_sel, prev_dimmed


def reconstruct_state(
    data: dict[str, Any],
    up_to_index: int | None,
) -> tuple[_GridMatrix, _GridMatrix, int, int, _Action | None]:
    """Reconstruct the game state up to a given action index.

    Args:
        data: The loaded match data (grid, actions, ...).
        up_to_index: Index (inclusive) of the last action to apply.
            ``None`` means the final state of the match; ``-1`` means the
            freshly started, empty board.

    Returns:
        Tuple of ``(user_sel, user_dimmed, hints_used, play_time, last_action)``.
    """
    if up_to_index is None:
        return (
            data["user_sel"],
            data["user_dimmed"],
            int(data.get("hints_used", 0)),
            int(data.get("play_time", 0)),
            None,
        )

    n = len(data["grid"])
    if up_to_index == -1:
        empty_sel = [[False] * n for _ in range(n)]
        empty_dimmed = [[False] * n for _ in range(n)]
        initial_action: _Action = {
            "type": "Start",
            "r": None,
            "c": None,
            "time": 0,
            "synthetic": True,
        }
        return empty_sel, empty_dimmed, 0, 0, initial_action

    actions = data.get("actions", [])
    if not actions:
        empty_sel = [[False] * n for _ in range(n)]
        empty_dimmed = [[False] * n for _ in range(n)]
        return empty_sel, empty_dimmed, 0, 0, None

    up_to_index = max(0, min(up_to_index, len(actions) - 1))

    user_sel: _GridMatrix = [[False] * n for _ in range(n)]
    user_dimmed: _GridMatrix = [[False] * n for _ in range(n)]
    hints_used = 0
    play_time = 0
    last_action: _Action | None = None

    for act in actions[: up_to_index + 1]:
        r, c = act.get("r"), act.get("c")
        if r is not None and c is not None:
            new_sel, new_dimmed = _derive_new_state(act)
            user_sel[r][c] = new_sel
            user_dimmed[r][c] = new_dimmed

        if act.get("type") == "Hint":
            hints_used += 1

        play_time = act.get("time", play_time)
        last_action = act

    if last_action is not None and "hints_used_so_far" in last_action:
        hints_used = last_action["hints_used_so_far"]

    return user_sel, user_dimmed, hints_used, play_time, last_action