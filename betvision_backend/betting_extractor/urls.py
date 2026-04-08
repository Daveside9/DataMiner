from django.urls import path
from . import views

urlpatterns = [
    path('sites/', views.get_supported_sites, name='betting_sites'),
    path('extract/', views.start_extraction, name='start_extraction'),
    path('status/<str:session_id>/', views.get_extraction_status, name='extraction_status'),
    path('stop/<str:session_id>/', views.stop_extraction, name='stop_extraction'),
    path('results/', views.get_all_results, name='all_results'),
    path('stats/', views.get_extraction_stats, name='extraction_stats'),
]