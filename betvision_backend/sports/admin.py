from django.contrib import admin
from .models import SportsMatch, SportsMonitoringSession, MatchPrediction, TeamAnalysis

@admin.register(SportsMatch)
class SportsMatchAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'away_team', 'sport', 'status', 'home_score', 'away_score', 'match_time']
    list_filter = ['sport', 'status', 'match_time']
    search_fields = ['home_team', 'away_team']
    ordering = ['-match_time']

@admin.register(SportsMonitoringSession)
class SportsMonitoringSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'sport', 'status', 'matches_found', 'predictions_generated', 'started_at']
    list_filter = ['sport', 'status', 'started_at']
    search_fields = ['user__username', 'teams_filter']
    ordering = ['-started_at']

@admin.register(MatchPrediction)
class MatchPredictionAdmin(admin.ModelAdmin):
    list_display = ['match', 'predicted_home_score', 'predicted_away_score', 'confidence_percentage', 'created_at']
    list_filter = ['confidence_percentage', 'created_at']
    search_fields = ['match__home_team', 'match__away_team']
    ordering = ['-created_at']

@admin.register(TeamAnalysis)
class TeamAnalysisAdmin(admin.ModelAdmin):
    list_display = ['team_name', 'sport', 'updated_at']
    list_filter = ['sport', 'updated_at']
    search_fields = ['team_name']
    ordering = ['-updated_at']