from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/increment-round/', views.increment_daily_round_count, name='increment_round'),
] 