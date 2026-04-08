from django.urls import path
from . import views

urlpatterns = [
    path('sessions/start/', views.start_monitoring_session, name='start_monitoring_session'),
    path('sessions/<int:session_id>/stop/', views.stop_monitoring_session, name='stop_monitoring_session'),
    path('sessions/<int:session_id>/pause/', views.pause_monitoring_session, name='pause_monitoring_session'),
    path('sessions/<int:session_id>/resume/', views.resume_monitoring_session, name='resume_monitoring_session'),
    path('sessions/', views.get_monitoring_sessions, name='get_monitoring_sessions'),
    path('sessions/<int:session_id>/', views.get_monitoring_session, name='get_monitoring_session'),
    path('sessions/<int:session_id>/screenshots/', views.get_session_screenshots, name='get_session_screenshots'),
    path('stats/', views.get_monitoring_stats, name='get_monitoring_stats'),
    path('alerts/', views.get_user_alerts, name='get_user_alerts'),
    path('alerts/<int:alert_id>/read/', views.mark_alert_read, name='mark_alert_read'),
]