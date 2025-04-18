from django.db import models
from django.utils import timezone
from django.db.models import UniqueConstraint

# Create your models here.

class DailyPomodoroStats(models.Model):
    user_id = models.UUIDField(db_index=True)
    date = models.DateField(db_index=True)
    completed_rounds = models.IntegerField(default=0)

    class Meta:
        # Ensure only one record per user per day
        constraints = [
            UniqueConstraint(fields=['user_id', 'date'], name='unique_user_date_stats')
        ]
        # Optional: Add ordering if needed when querying multiple days
        # ordering = ['user_id', '-date']

    def __str__(self):
        return f"Stats for {self.user_id} on {self.date}: {self.completed_rounds} rounds"
