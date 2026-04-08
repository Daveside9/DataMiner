from django.contrib import admin
from .models import BettingSite, ExtractionSession, MatchResult, ExtractionConfig

@admin.register(BettingSite)
class BettingSiteAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'login_required', 'active', 'created_at']
    list_filter = ['login_required', 'active']
    search_fields = ['name', 'url']

@admin.register(ExtractionSession)
class ExtractionSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'site', 'status', 'matches_found', 'start_time']
    list_filter = ['status', 'site', 'start_time']
    search_fields = ['session_id', 'user__username', 'site__name']
    readonly_fields = ['session_id', 'start_time', 'end_time']

@admin.register(MatchResult)
class MatchResultAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'away_team', 'home_score', 'away_score', 'date', 'confidence_score']
    list_filter = ['result_type', 'competition', 'date', 'session__site']
    search_fields = ['home_team', 'away_team', 'competition']
    readonly_fields = ['extracted_at']

@admin.register(ExtractionConfig)
class ExtractionConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'ocr_engine', 'headless_mode', 'created_at']
    list_filter = ['ocr_engine', 'headless_mode']
    search_fields = ['user__username']