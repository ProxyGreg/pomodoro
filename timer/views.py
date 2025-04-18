from django.shortcuts import render

# Create your views here.

def index(request):
    """Renders the main Pomodoro timer page."""
    return render(request, 'timer/index.html')
