from django.urls import path
from . import views

urlpatterns = [
    path('start-monitoring/', views.start_sports_monitoring, name='start_sports_monitoring'),
    path('stop-monitoring/<int:session_id>/', views.stop_sports_monitoring, name='stop_sports_monitoring'),
    path('live-matches/', views.get_live_matches, name='get_live_matches'),
    path('predict/', views.generate_match_prediction, name='generate_match_prediction'),
    path('analyze-team/', views.analyze_team, name='analyze_team'),
    path('sessions/', views.get_user_sports_sessions, name='get_user_sports_sessions'),
    path('stats/', views.get_sports_stats, name='get_sports_stats'),
]