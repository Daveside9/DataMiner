from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
import threading
import time
import uuid
from .models import BettingSite, ExtractionSession, MatchResult, ExtractionConfig
from .serializers import (
    BettingSiteSerializer, ExtractionSessionSerializer, 
    MatchResultSerializer, ExtractionConfigSerializer
)

# Global dictionary to store active extractions
active_extractions = {}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_supported_sites(request):
    """Get list of supported betting sites"""
    sites = BettingSite.objects.filter(active=True)
    serializer = BettingSiteSerializer(sites, many=True)
    return Response({'sites': serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_extraction(request):
    """Start a new betting history extraction"""
    try:
        data = request.data
        
        # Validate required fields
        if not data.get('site'):
            return Response({'error': 'Site is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get betting site
        try:
            site = BettingSite.objects.get(id=data['site'])
        except BettingSite.DoesNotExist:
            return Response({'error': 'Invalid site'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create extraction session
        session = ExtractionSession.objects.create(
            session_id=session_id,
            user=request.user,
            site=site,
            max_matches=data.get('max_matches', 25),
            status='starting',
            message='Initializing extraction...'
        )
        
        # Prepare extraction parameters
        extraction_params = {
            'session_id': session_id,
            'site_name': site.name.lower().replace(' ', ''),
            'max_matches': data.get('max_matches', 25),
            'ocr_engine': data.get('ocr_engine', 'easyocr'),
            'headless_mode': data.get('headless_mode', False),
            'save_screenshots': data.get('save_screenshots', True),
            'image_processing': {
                'enhance_contrast': data.get('enhance_contrast', True),
                'denoise': data.get('denoise', True),
                'sharpen': data.get('sharpen', True),
                'threshold': data.get('threshold', True)
            }
        }
        
        # Add credentials if provided
        credentials = None
        if data.get('username') and data.get('password'):
            credentials = {
                'username': data['username'],
                'password': data['password']
            }
        
        # Store in active extractions
        active_extractions[session_id] = {
            'session': session,
            'status': 'starting',
            'progress': 0,
            'message': 'Initializing extraction...',
            'matches_found': 0,
            'errors': []
        }
        
        # Start extraction in background thread
        thread = threading.Thread(
            target=run_extraction,
            args=(session_id, extraction_params, credentials)
        )
        thread.daemon = True
        thread.start()
        
        return Response({
            'session_id': session_id,
            'status': 'started',
            'message': 'Extraction started successfully'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_extraction_status(request, session_id):
    """Get status of an extraction session"""
    try:
        session = get_object_or_404(ExtractionSession, session_id=session_id, user=request.user)
        
        # Get from active extractions if running
        if session_id in active_extractions:
            active_data = active_extractions[session_id]
            return Response({
                'session_id': session_id,
                'status': active_data['status'],
                'progress': active_data['progress'],
                'message': active_data['message'],
                'matches_found': active_data['matches_found'],
                'start_time': session.start_time.isoformat(),
                'site_name': session.site.name
            })
        
        # Return session data from database
        serializer = ExtractionSessionSerializer(session)
        response_data = serializer.data
        
        # Add results if completed
        if session.status == 'completed':
            results = MatchResult.objects.filter(session=session)
            results_serializer = MatchResultSerializer(results, many=True)
            response_data['results'] = results_serializer.data
        
        return Response(response_data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_extraction(request, session_id):
    """Stop an active extraction"""
    try:
        session = get_object_or_404(ExtractionSession, session_id=session_id, user=request.user)
        
        # Update session status
        session.status = 'stopped'
        session.message = 'Extraction stopped by user'
        session.end_time = timezone.now()
        session.save()
        
        # Update active extractions
        if session_id in active_extractions:
            active_extractions[session_id]['status'] = 'stopped'
            active_extractions[session_id]['message'] = 'Extraction stopped by user'
        
        return Response({'message': 'Extraction stopped'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_results(request):
    """Get all extraction results for the user"""
    try:
        results = MatchResult.objects.filter(
            session__user=request.user
        ).order_by('-extracted_at')[:100]
        
        serializer = MatchResultSerializer(results, many=True)
        return Response({'results': serializer.data})
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_extraction_stats(request):
    """Get extraction statistics for the user"""
    try:
        user_results = MatchResult.objects.filter(session__user=request.user)
        
        total_matches = user_results.count()
        successful_matches = user_results.filter(confidence_score__gt=0.5).count()
        success_rate = (successful_matches / total_matches * 100) if total_matches > 0 else 0
        
        avg_confidence = user_results.aggregate(
            avg_confidence=models.Avg('confidence_score')
        )['avg_confidence'] or 0
        avg_confidence = avg_confidence * 100
        
        sites_used = user_results.values('session__site').distinct().count()
        
        return Response({
            'total_matches': total_matches,
            'success_rate': round(success_rate, 1),
            'avg_confidence': round(avg_confidence, 1),
            'sites_used': sites_used,
            'sites_supported': BettingSite.objects.filter(active=True).count()
        })
        
    except Exception as e:
        return Response({
            'total_matches': 0,
            'success_rate': 0,
            'avg_confidence': 0,
            'sites_used': 0,
            'sites_supported': 5
        })

def run_extraction(session_id, params, credentials):
    """Run extraction in background thread"""
    try:
        # Get session
        session = ExtractionSession.objects.get(session_id=session_id)
        
        # Update status
        session.status = 'running'
        session.message = 'Starting browser...'
        session.progress = 10
        session.save()
        
        active_extractions[session_id].update({
            'status': 'running',
            'message': 'Starting browser...',
            'progress': 10
        })
        
        # Simulate extraction process (replace with actual extraction logic)
        import random
        
        steps = [
            ('Navigating to site...', 30),
            ('Capturing screenshots...', 50),
            ('Processing images with OCR...', 70),
            ('Extracting match data...', 90),
            ('Saving results...', 100)
        ]
        
        for message, progress in steps:
            if session_id not in active_extractions or active_extractions[session_id]['status'] == 'stopped':
                break
                
            time.sleep(2)  # Simulate processing time
            
            session.message = message
            session.progress = progress
            session.save()
            
            active_extractions[session_id].update({
                'message': message,
                'progress': progress
            })
        
        # Generate sample results (replace with actual extraction)
        if session_id in active_extractions and active_extractions[session_id]['status'] != 'stopped':
            teams = [
                'Manchester United', 'Liverpool', 'Chelsea', 'Arsenal', 'Manchester City',
                'Tottenham', 'Newcastle', 'Brighton', 'West Ham', 'Aston Villa'
            ]
            
            num_matches = min(params['max_matches'], random.randint(5, 15))
            
            for i in range(num_matches):
                home_team = random.choice(teams)
                away_team = random.choice([t for t in teams if t != home_team])
                home_score = random.randint(0, 4)
                away_score = random.randint(0, 4)
                
                result_type = 'home_win' if home_score > away_score else 'away_win' if away_score > home_score else 'draw'
                
                MatchResult.objects.create(
                    session=session,
                    match_id=f'match_{session_id}_{i}',
                    date=timezone.now().date(),
                    home_team=home_team,
                    away_team=away_team,
                    home_score=home_score,
                    away_score=away_score,
                    competition='Premier League',
                    result_type=result_type,
                    confidence_score=0.7 + random.random() * 0.3,
                    screenshot_path=f'screenshot_{i}.png'
                )
            
            # Update final status
            session.status = 'completed'
            session.message = f'Extraction completed! Found {num_matches} matches.'
            session.progress = 100
            session.matches_found = num_matches
            session.end_time = timezone.now()
            session.save()
            
            active_extractions[session_id].update({
                'status': 'completed',
                'message': f'Extraction completed! Found {num_matches} matches.',
                'progress': 100,
                'matches_found': num_matches
            })
        
    except Exception as e:
        # Update error status
        session.status = 'error'
        session.message = f'Extraction failed: {str(e)}'
        session.error_message = str(e)
        session.end_time = timezone.now()
        session.save()
        
        if session_id in active_extractions:
            active_extractions[session_id].update({
                'status': 'error',
                'message': f'Extraction failed: {str(e)}',
                'errors': [str(e)]
            })