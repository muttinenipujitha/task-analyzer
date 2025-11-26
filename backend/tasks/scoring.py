from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple, Set


@dataclass
class ScoredTask:
    raw: Dict[str, Any]
    id: str
    score: float
    priority_label: str
    explanation: str
    strategy: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def _parse_date(value: Any) -> Optional[date]:
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        # Expecting ISO format YYYY-MM-DD
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except Exception:
        return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _build_id(task: Dict[str, Any], fallback_index: int) -> str:
    # Prefer explicit id, then title, then index
    if "id" in task and task["id"]:
        return str(task["id"])
    if task.get("title"):
        return f"{task['title']}#{fallback_index}"
    return f"task-{fallback_index}"


def _detect_cycles(graph: Dict[str, List[str]]) -> Set[str]:
    """Return set of node ids that participate in any cycle."""
    visited: Set[str] = set()
    in_stack: Set[str] = set()
    cycle_nodes: Set[str] = set()

    def dfs(node: str):
        if node in in_stack:
            cycle_nodes.add(node)
            return
        if node in visited:
            return
        visited.add(node)
        in_stack.add(node)
        for neigh in graph.get(node, []):
            dfs(neigh)
        in_stack.remove(node)

    for node in graph.keys():
        if node not in visited:
            dfs(node)
    # We only found the entry points; mark all reachable from them as "in cycle-ish"
    # so users know those tasks are risky. This is a bit conservative but clear.
    expanded: Set[str] = set()

    def mark(node: str):
        if node in expanded:
            return
        expanded.add(node)
        for neigh in graph.get(node, []):
            mark(neigh)

    for node in list(cycle_nodes):
        mark(node)
    return expanded or cycle_nodes


def _normalise_urgency(due: Optional[date], today: Optional[date] = None) -> Tuple[float, bool]:
    if today is None:
        today = date.today()
    if not due:
        return 0.0, False
    delta_days = (due - today).days
    if delta_days < 0:
        # Past due: treat as very urgent
        return 1.0, True
    # Within next 30 days fades from 1 -> 0
    if delta_days >= 30:
        return 0.0, False
    urgency = max(0.0, 1.0 - (delta_days / 30.0))
    return urgency, False


def _normalise_importance(importance: Any) -> float:
    val = _safe_int(importance, 0)
    if val < 0:
        val = 0
    if val > 10:
        val = 10
    return val / 10.0


def _normalise_effort(estimated_hours: Any) -> float:
    """Return higher score for lower effort ("quick wins")."""
    hours = _safe_float(estimated_hours, 0.0)
    if hours <= 0:
        return 1.0
    # Cap at 16 hours (~2 working days)
    capped = min(hours, 16.0)
    return max(0.0, 1.0 - capped / 16.0)


def _build_dependency_graph(tasks: List[Dict[str, Any]]) -> Tuple[Dict[str, List[str]], Dict[str, int]]:
    graph: Dict[str, List[str]] = {}
    reverse_counts: Dict[str, int] = {}

    id_map: Dict[int, str] = {}
    for idx, t in enumerate(tasks):
        tid = _build_id(t, idx)
        id_map[idx] = tid
        graph.setdefault(tid, [])
        reverse_counts.setdefault(tid, 0)

    for idx, t in enumerate(tasks):
        tid = id_map[idx]
        deps_raw = t.get("dependencies") or []
        if isinstance(deps_raw, (str, int)):
            deps_raw = [deps_raw]
        deps: List[str] = []
        for dep in deps_raw:
            dep_id = str(dep)
            if dep_id in graph:
                deps.append(dep_id)
                reverse_counts[dep_id] = reverse_counts.get(dep_id, 0) + 1
        graph[tid] = deps

    return graph, reverse_counts


def _priority_label(score: float) -> str:
    if score >= 75:
        return "High"
    if score >= 45:
        return "Medium"
    return "Low"


def _strategy_weights(strategy: str) -> Tuple[float, float, float, float]:
    """Return weights (urgency, importance, effort_quick_win, dependency_breadth)."""
    s = (strategy or "smart_balance").lower()
    if s == "fastest_wins":
        return 0.2, 0.2, 0.6, 0.0
    if s == "high_impact":
        return 0.2, 0.7, 0.0, 0.1
    if s == "deadline_driven":
        return 0.7, 0.2, 0.1, 0.0
    # default smart balance
    return 0.35, 0.35, 0.15, 0.15


def score_tasks(
    tasks: List[Dict[str, Any]],
    strategy: str = "smart_balance",
) -> List[ScoredTask]:
    if not isinstance(tasks, list):
        raise ValueError("tasks must be a list")

    graph, reverse_counts = _build_dependency_graph(tasks)
    circular_nodes = _detect_cycles(graph) if graph else set()

    weights = _strategy_weights(strategy)
    w_urgency, w_importance, w_effort, w_dep = weights

    max_reverse = max(reverse_counts.values()) if reverse_counts else 0 or 1

    today = date.today()
    scored: List[ScoredTask] = []

    for idx, raw in enumerate(tasks):
        tid = _build_id(raw, idx)
        title = raw.get("title") or f"Task {idx + 1}"

        due = _parse_date(raw.get("due_date"))
        urgency, is_past_due = _normalise_urgency(due, today=today)
        importance = _normalise_importance(raw.get("importance"))
        effort_quick = _normalise_effort(raw.get("estimated_hours"))
        deps_breadth = reverse_counts.get(tid, 0) / max_reverse if max_reverse else 0.0

        base_score = (
            w_urgency * urgency
            + w_importance * importance
            + w_effort * effort_quick
            + w_dep * deps_breadth
        )

        # Slight bonus for past-due tasks so they bubble up
        if is_past_due:
            base_score += 0.1

        # Bound to [0, 1]
        base_score = max(0.0, min(1.0, base_score))

        # Convert to 0–100 scale
        final_score = round(base_score * 100.0, 2)
        label = _priority_label(final_score)

        # Build human-readable explanation
        reasons = []
        if is_past_due:
            reasons.append("due date is in the past")
        elif urgency > 0.7:
            reasons.append("deadline is very close")
        elif urgency > 0.3:
            reasons.append("deadline is approaching")

        if importance >= 0.7:
            reasons.append("marked as highly important")
        elif importance <= 0.3:
            reasons.append("marked as lower importance")

        if effort_quick >= 0.7:
            reasons.append("can be completed quickly (quick win)")
        elif effort_quick <= 0.3:
            reasons.append("requires significant effort")

        if deps_breadth > 0.5:
            reasons.append("unblocks several other tasks")
        elif deps_breadth > 0.0:
            reasons.append("unblocks at least one other task")

        if tid in circular_nodes:
            reasons.append("participates in a circular dependency – review dependencies")

        if not reasons:
            reasons.append("balanced trade-off between urgency, impact and effort")

        explanation = f"{title} is ranked as {label} priority because " + ", ".join(reasons) + "."

        scored.append(
            ScoredTask(
                raw=raw,
                id=tid,
                score=final_score,
                priority_label=label,
                explanation=explanation,
                strategy=strategy,
                metadata={
                    "urgency": round(urgency, 3),
                    "importance": round(importance, 3),
                    "effort_quick_win": round(effort_quick, 3),
                    "dependency_breadth": round(deps_breadth, 3),
                    "is_past_due": is_past_due,
                    "is_in_circular_dependency": tid in circular_nodes,
                },
            )
        )

    # Sort descending by score, then by importance, then by urgency
    scored.sort(
        key=lambda t: (
            t.score,
            t.metadata.get("importance", 0.0),
            t.metadata.get("urgency", 0.0),
        ),
        reverse=True,
    )
    return scored


def analyze_tasks(tasks: List[Dict[str, Any]], strategy: str = "smart_balance") -> List[Dict[str, Any]]:
    scored = score_tasks(tasks, strategy=strategy)
    enriched: List[Dict[str, Any]] = []
    for t in scored:
        data = dict(t.raw)
        data.update(
            {
                "calculated_score": t.score,
                "priority_label": t.priority_label,
                "strategy": t.strategy,
                "explanation": t.explanation,
                "metadata": t.metadata,
            }
        )
        enriched.append(data)
    return enriched


def suggest_top_tasks(
    tasks: List[Dict[str, Any]],
    strategy: str = "smart_balance",
    limit: int = 3,
) -> List[Dict[str, Any]]:
    analyzed = analyze_tasks(tasks, strategy=strategy)
    return analyzed[: max(1, limit)]
