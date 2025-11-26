from typing import List

from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .scoring import analyze_tasks, suggest_top_tasks
from .serializers import (
    AnalyzeRequestSerializer,
    AnalyzeResponseTaskSerializer,
    SuggestQuerySerializer,
    SuggestResponseSerializer,
)


CACHE_KEY_LAST_TASKS = "tasks:last_payload"


@api_view(["POST"])
def analyze_tasks_view(request):
    """
    Accepts a JSON body of the form:
    {
        "strategy": "smart_balance" | "fastest_wins" | "high_impact" | "deadline_driven",
        "tasks": [ { ...task fields... } ]
    }

    and returns the same tasks enriched with a calculated score,
    priority label and human-readable explanation.
    """
    serializer = AnalyzeRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    strategy = serializer.validated_data.get("strategy") or "smart_balance"
    tasks = serializer.validated_data["tasks"]

    # Use the raw dicts for scoring (DRF gives OrderedDict instances)
    plain_tasks: List[dict] = [dict(t) for t in tasks]

    analyzed = analyze_tasks(plain_tasks, strategy=strategy)

    # Persist the last analyzed payload so /suggest/ can work off it
    cache.set(CACHE_KEY_LAST_TASKS, plain_tasks, timeout=60 * 60)  # 1 hour

    response_serializer = AnalyzeResponseTaskSerializer(analyzed, many=True)
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def suggest_tasks_view(request):
    """
    Returns the top N tasks (default 3) based on the *last analyzed*
    set of tasks. This keeps the API simple for the assignment while
    still behaving like a "what should I do next?" helper.

    Optional query params:
    - strategy: one of the known strategies
    - limit: number of tasks to return (default 3)
    """
    query_serializer = SuggestQuerySerializer(data=request.query_params)
    if not query_serializer.is_valid():
        return Response(query_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    strategy = query_serializer.validated_data.get("strategy") or "smart_balance"
    limit = query_serializer.validated_data.get("limit") or 3

    last_tasks = cache.get(CACHE_KEY_LAST_TASKS)
    if not last_tasks:
        return Response(
            {
                "detail": (
                    "No tasks have been analyzed yet. "
                    "Call POST /api/tasks/analyze/ first with your task list."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    suggested = suggest_top_tasks(last_tasks, strategy=strategy, limit=limit)
    response_serializer = SuggestResponseSerializer({"tasks": suggested})
    return Response(response_serializer.data, status=status.HTTP_200_OK)
