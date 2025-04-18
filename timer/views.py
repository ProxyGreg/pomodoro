from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt # Or ensure CSRF token is sent from JS
from django.utils import timezone
from .models import DailyPomodoroStats
import uuid
from datetime import timedelta # Add timedelta

# Create your views here.

def index(request):
    """Renders the main Pomodoro timer page and fetches stats for the chart."""
    user_id = getattr(request, 'pomodoro_user_id', None)
    chart_labels = []
    chart_data = []

    if user_id:
        today = timezone.now().date()
        # Get the last 5 dates (today and previous 4)
        dates = [today - timedelta(days=i) for i in range(5)]
        
        try:
            # Query stats for these dates
            stats = DailyPomodoroStats.objects.filter(
                user_id=user_id, 
                date__in=dates
            ).order_by('date') # Order chronologically for processing
            
            # Create a dictionary for quick lookups: date_str -> count
            stats_dict = {s.date.strftime('%Y-%m-%d'): s.completed_rounds for s in stats}
            
            # Prepare labels and data for the chart (reversed for display order)
            chart_labels = [d.strftime('%a, %b %d') for d in reversed(dates)] # e.g., "Fri, Apr 18"
            chart_data = [stats_dict.get(d.strftime('%Y-%m-%d'), 0) for d in reversed(dates)]

        except Exception as e:
            # Log error e - couldn't fetch stats, default to empty chart
            print(f"Error fetching chart data for user {user_id}: {e}") # Basic logging
            pass 

    context = {
        # Pass data needed for Chart.js
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'timer/index.html', context)

# Simple CSRF exemption for API for now; sending token from JS is better practice
@csrf_exempt 
@require_POST
def increment_daily_round_count(request):
    """Increments the completed round count for the user for today."""
    user_id = getattr(request, 'pomodoro_user_id', None)

    if not user_id or not isinstance(user_id, uuid.UUID):
        return JsonResponse({'status': 'error', 'message': 'Invalid or missing user ID.'}, status=400)

    today = timezone.now().date()

    try:
        stats, created = DailyPomodoroStats.objects.get_or_create(
            user_id=user_id,
            date=today,
            defaults={'completed_rounds': 1} # Start at 1 if created
        )

        if not created:
            stats.completed_rounds += 1
            stats.save()

        return JsonResponse({'status': 'success', 'rounds_today': stats.completed_rounds})
    except Exception as e:
        # Log the error e
        print(f"Error incrementing stats for user {user_id}: {e}") # Basic logging
        return JsonResponse({'status': 'error', 'message': 'Could not update stats.'}, status=500)
