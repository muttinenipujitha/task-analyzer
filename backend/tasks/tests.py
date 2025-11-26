from datetime import date, timedelta

from django.test import TestCase

from .scoring import analyze_tasks, suggest_top_tasks


class ScoringAlgorithmTests(TestCase):
    def test_high_importance_beats_low_when_other_factors_equal(self):
        base_due = (date.today() + timedelta(days=3)).isoformat()
        tasks = [
            {
                "id": "low",
                "title": "Low importance task",
                "due_date": base_due,
                "estimated_hours": 3,
                "importance": 3,
                "dependencies": [],
            },
            {
                "id": "high",
                "title": "High importance task",
                "due_date": base_due,
                "estimated_hours": 3,
                "importance": 9,
                "dependencies": [],
            },
        ]

        analyzed = analyze_tasks(tasks, strategy="high_impact")
        self.assertEqual(analyzed[0]["id"], "high")
        self.assertGreater(
            analyzed[0]["calculated_score"],
            analyzed[1]["calculated_score"],
        )

    def test_past_due_tasks_are_more_urgent(self):
        past_due = (date.today() - timedelta(days=1)).isoformat()
        future_due = (date.today() + timedelta(days=10)).isoformat()

        tasks = [
            {
                "id": "future",
                "title": "Future task",
                "due_date": future_due,
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": [],
            },
            {
                "id": "past",
                "title": "Past due task",
                "due_date": past_due,
                "estimated_hours": 2,
                "importance": 5,
                "dependencies": [],
            },
        ]

        analyzed = analyze_tasks(tasks, strategy="deadline_driven")
        self.assertEqual(analyzed[0]["id"], "past")
        self.assertTrue(analyzed[0]["metadata"]["is_past_due"])

    def test_circular_dependencies_are_detected(self):
        due = (date.today() + timedelta(days=5)).isoformat()
        tasks = [
            {
                "id": "A",
                "title": "Task A",
                "due_date": due,
                "estimated_hours": 1,
                "importance": 5,
                "dependencies": ["B"],
            },
            {
                "id": "B",
                "title": "Task B",
                "due_date": due,
                "estimated_hours": 1,
                "importance": 5,
                "dependencies": ["A"],
            },
        ]

        analyzed = analyze_tasks(tasks)
        ids_with_cycle_flag = {
            t["id"]
            for t in analyzed
            if t["metadata"]["is_in_circular_dependency"]
        }
        self.assertEqual(ids_with_cycle_flag, {"A", "B"})

    def test_suggest_top_tasks_respects_limit(self):
        due = (date.today() + timedelta(days=2)).isoformat()
        tasks = []
        for i in range(5):
            tasks.append(
                {
                    "id": f"T{i}",
                    "title": f"Task {i}",
                    "due_date": due,
                    "estimated_hours": i + 1,
                    "importance": 10 - i,
                    "dependencies": [],
                }
            )

        top_two = suggest_top_tasks(tasks, limit=2)
        self.assertEqual(len(top_two), 2)
