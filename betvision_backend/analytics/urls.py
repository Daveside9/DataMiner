from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.get_dashboard_data, name='get_dashboard_data'),
    path('user/', views.get_user_analytics, name='get_user_analytics'),
    path('platform/', views.get_platform_metrics, name='get_platform_metrics'),
]