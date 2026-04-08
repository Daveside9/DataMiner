from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import SportsMatch, SportsMonitoringSession, MatchPrediction, TeamAnalysis
from .serializers import (
    SportsMatchSerializer,
    SportsMonitoringSessionSerializer,
    MatchPredictionSerializer,
    TeamAnalysisSerializer
)
import subprocess
import threading
import requests
import json
from datetime import datetime, timedelta

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def start_sports_monitoring(request):
    """Start a new sports monitoring session"""
    user = request.user
    data = request.data
    
    # Create monitoring session
    session = SportsMonitoringSession.objects.create(
        user=user,
        sport=data.get('sport', 'football'),
        source_url=data.get('source_url', 'https://www.flashscore.com/football/'),
        teams_filter=data.get('teams_filter', ''),
        interval_seconds=data.get('interval_seconds', 60),
        duration_minutes=data.get('duration_minutes', 30)
    )
    
    # Start background monitoring
    thread = threading.Thread(
        target=start_background_sports_monitoring,
        args=(session.id,)
    )
    thread.daemon = True
    thread.start()
    
    return Response({
        'success': True,
        'message': 'Sports monitoring started',
        'session_id': session.id,
        'session': SportsMonitoringSessionSerializer(session).data
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def stop_sports_monitoring(request, session_id):
    """Stop a sports monitoring session"""
    session = get_object_or_404(SportsMonitoringSession, id=session_id, user=request.user)
    
    session.status = 'completed'
    session.ended_at = timezone.now()
    session.save()
    
    return Response({
        'success': True,
        'message': 'Sports monitoring stopped',
        'session': SportsMonitoringSessionSerializer(session).data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_live_matches(request):
    """Get live sports matches"""
    sport = request.GET.get('sport', 'football')
    
    # Get recent matches (last 2 hours)
    recent_matches = SportsMatch.objects.filter(
        sport=sport,
        updated_at__gte=timezone.now() - timedelta(hours=2)
    ).order_by('-updated_at')[:20]
    
    return Response({
        'success': True,
        'matches': SportsMatchSerializer(recent_matches, many=True).data,
        'count': recent_matches.count()
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_match_prediction(request):
    """Generate AI prediction for a match"""
    match_id = request.data.get('match_id')
    session_id = request.data.get('session_id')
    
    match = get_object_or_404(SportsMatch, id=match_id)
    session = get_object_or_404(SportsMonitoringSession, id=session_id, user=request.user)
    
    # Generate prediction using AI logic
    prediction_data = generate_ai_prediction(match)
    
    # Save prediction
    prediction = MatchPrediction.objects.create(
        match=match,
        session=session,
        predicted_home_score=prediction_data['predicted_home_score'],
        predicted_away_score=prediction_data['predicted_away_score'],
        confidence_percentage=prediction_data['confidence'],
        reasoning=prediction_data['reasoning'],
        prediction_factors=prediction_data['factors']
    )
    
    session.predictions_generated += 1
    session.save()
    
    return Response({
        'success': True,
        'prediction': MatchPredictionSerializer(prediction).data
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def analyze_team(request):
    """Analyze a specific team"""
    team_name = request.data.get('team_name')
    sport = request.data.get('sport', 'football')
    
    if not team_name:
        return Response({
            'success': False,
            'error': 'Team name is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Try to get existing analysis
    try:
        analysis = TeamAnalysis.objects.get(team_name=team_name, sport=sport)
        
        # Update if older than 1 hour
        if analysis.updated_at < timezone.now() - timedelta(hours=1):
            analysis_data = perform_team_analysis(team_name, sport)
            analysis.analysis_data = analysis_data
            analysis.save()
    except TeamAnalysis.DoesNotExist:
        # Create new analysis
        analysis_data = perform_team_analysis(team_name, sport)
        analysis = TeamAnalysis.objects.create(
            team_name=team_name,
            sport=sport,
            analysis_data=analysis_data
        )
    
    return Response({
        'success': True,
        'analysis': TeamAnalysisSerializer(analysis).data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_sports_sessions(request):
    """Get user's sports monitoring sessions"""
    sessions = SportsMonitoringSession.objects.filter(user=request.user).order_by('-started_at')
    
    return Response({
        'success': True,
        'sessions': SportsMonitoringSessionSerializer(sessions, many=True).data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_sports_stats(request):
    """Get user's sports monitoring statistics"""
    user = request.user
    
    total_sessions = user.sports_sessions.count()
    active_sessions = user.sports_sessions.filter(status='active').count()
    total_matches = SportsMatch.objects.filter(
        predictions__session__user=user
    ).distinct().count()
    total_predictions = MatchPrediction.objects.filter(session__user=user).count()
    
    # Calculate accuracy (simplified)
    correct_predictions = 0
    total_evaluated = 0
    
    for prediction in MatchPrediction.objects.filter(session__user=user):
        match = prediction.match
        if match.status == 'finished':
            total_evaluated += 1
            if (prediction.predicted_home_score > prediction.predicted_away_score and 
                match.home_score > match.away_score) or \
               (prediction.predicted_home_score < prediction.predicted_away_score and 
                match.home_score < match.away_score) or \
               (prediction.predicted_home_score == prediction.predicted_away_score and 
                match.home_score == match.away_score):
                correct_predictions += 1
    
    accuracy = (correct_predictions / total_evaluated * 100) if total_evaluated > 0 else 0
    
    return Response({
        'success': True,
        'stats': {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'total_matches_monitored': total_matches,
            'total_predictions': total_predictions,
            'prediction_accuracy': round(accuracy, 1),
            'correct_predictions': correct_predictions,
            'total_evaluated': total_evaluated
        }
    }, status=status.HTTP_200_OK)

def start_background_sports_monitoring(session_id):
    """Start background sports monitoring process"""
    try:
        session = SportsMonitoringSession.objects.get(id=session_id)
        
        # Call the real-time sports system
        response = requests.post('http://localhost:5001/api/start-monitoring', json={
            'url': session.source_url,
            'duration': session.duration_minutes,
            'interval': session.interval_seconds,
            'specific_teams': session.teams_filter.split(',') if session.teams_filter else []
        })
        
        if response.status_code == 200:
            print(f"✅ Background sports monitoring started for session {session_id}")
        else:
            session.status = 'failed'
            session.save()
            print(f"❌ Failed to start background monitoring for session {session_id}")
            
    except Exception as e:
        print(f"❌ Background monitoring error: {e}")
        try:
            session = SportsMonitoringSession.objects.get(id=session_id)
            session.status = 'failed'
            session.save()
        except:
            pass

def generate_ai_prediction(match):
    """Generate AI prediction for a match"""
    # Simplified AI prediction logic
    # In a real implementation, this would use machine learning models
    
    import random
    
    # Base prediction on team names and current scores
    home_advantage = 0.1  # 10% home advantage
    
    # Simulate team strength (in real implementation, this would come from historical data)
    home_strength = random.uniform(0.3, 0.9)
    away_strength = random.uniform(0.3, 0.9)
    
    # Apply home advantage
    home_strength += home_advantage
    
    # Predict scores
    if home_strength > away_strength:
        predicted_home = random.randint(1, 3)
        predicted_away = random.randint(0, 2)
        confidence = min(90, 60 + (home_strength - away_strength) * 50)
        reasoning = "Home team has statistical advantage"
    elif away_strength > home_strength:
        predicted_home = random.randint(0, 2)
        predicted_away = random.randint(1, 3)
        confidence = min(90, 60 + (away_strength - home_strength) * 50)
        reasoning = "Away team has statistical advantage"
    else:
        predicted_home = random.randint(1, 2)
        predicted_away = random.randint(1, 2)
        confidence = random.randint(50, 70)
        reasoning = "Teams are evenly matched"
    
    return {
        'predicted_home_score': predicted_home,
        'predicted_away_score': predicted_away,
        'confidence': confidence,
        'reasoning': reasoning,
        'factors': {
            'home_strength': home_strength,
            'away_strength': away_strength,
            'home_advantage': home_advantage
        }
    }

def perform_team_analysis(team_name, sport):
    """Perform comprehensive team analysis"""
    # Simplified team analysis
    # In a real implementation, this would scrape historical data
    
    import random
    
    analysis = {
        'team_name': team_name,
        'sport': sport,
        'recent_form': {
            'wins': random.randint(3, 8),
            'draws': random.randint(0, 3),
            'losses': random.randint(0, 4),
            'goals_scored': random.randint(10, 25),
            'goals_conceded': random.randint(5, 20)
        },
        'key_stats': {
            'win_percentage': random.randint(40, 80),
            'avg_goals_per_game': round(random.uniform(1.0, 3.0), 1),
            'clean_sheets': random.randint(2, 8),
            'home_record': f"{random.randint(3, 6)}W-{random.randint(0, 2)}D-{random.randint(0, 3)}L",
            'away_record': f"{random.randint(2, 5)}W-{random.randint(0, 3)}D-{random.randint(0, 4)}L"
        },
        'strengths': [
            'Strong attacking play',
            'Solid defense',
            'Good set piece conversion'
        ],
        'weaknesses': [
            'Inconsistent away form',
            'Vulnerable to counter-attacks'
        ],
        'next_match_prediction': {
            'confidence': random.randint(60, 85),
            'expected_result': random.choice(['Win', 'Draw', 'Loss'])
        }
    }
    
    return analysis