from rest_framework import serializers
from .models import BettingSite, ExtractionSession, MatchResult, ExtractionConfig

class BettingSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BettingSite
        fields = ['id', 'name', 'url', 'login_required', 'active']

class ExtractionSessionSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.name', read_only=True)
    
    class Meta:
        model = ExtractionSession
        fields = [
            'session_id', 'site_name', 'status', 'progress', 'message',
            'max_matches', 'matches_found', 'start_time', 'end_time', 'error_message'
        ]

class MatchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchResult
        fields = [
            'match_id', 'date', 'home_team', 'away_team', 'home_score', 'away_score',
            'competition', 'result_type', 'confidence_score', 'screenshot_path',
            'betting_odds', 'extracted_at'
        ]

class ExtractionConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractionConfig
        fields = [
            'ocr_engine', 'enhance_contrast', 'denoise', 'sharpen', 'threshold',
            'headless_mode', 'save_screenshots'
        ]