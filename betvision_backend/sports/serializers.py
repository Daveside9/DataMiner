from rest_framework import serializers
from .models import SportsMatch, SportsMonitoringSession, MatchPrediction, TeamAnalysis

class SportsMatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportsMatch
        fields = '__all__'

class SportsMonitoringSessionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = SportsMonitoringSession
        fields = '__all__'

class MatchPredictionSerializer(serializers.ModelSerializer):
    match = SportsMatchSerializer(read_only=True)
    
    class Meta:
        model = MatchPrediction
        fields = '__all__'

class TeamAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamAnalysis
        fields = '__all__'