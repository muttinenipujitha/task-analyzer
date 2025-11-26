from django.db import models

class Task(models.Model):
    """
    Basic Task model.
    For this assignment the scoring algorithm works on in-memory payloads,
    but this model shows how tasks would be persisted in a real system.
    """
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.FloatField(null=True, blank=True)
    importance = models.PositiveIntegerField(default=5)  # 1–10
    # self-referential dependencies, optional
    dependencies = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='blocked_by'
    )

    def __str__(self):
        return self.title
