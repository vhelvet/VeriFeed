from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Count, Q
from .models import Review
from .serializers import ReviewSerializer

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_review_stats(request):
    """Get review statistics for the current user"""
    user = request.user
    reviews = Review.objects.filter(user=user)
    
    stats = {
        'total_reviews': reviews.count(),
        'average_rating_given': reviews.aggregate(avg=Avg('rating'))['avg'] or 0,
        'recent_reviews': reviews.order_by('-created_at')[:5].count(),
        'verified_reviews': reviews.filter(is_verified=True).count(),
    }
    
    return Response(stats)

@api_view(['GET'])
def service_review_summary(request, service_name):
    """Get review summary for a specific service"""
    reviews = Review.objects.filter(service_name__iexact=service_name)
    
    if not reviews.exists():
        return Response({
            'service_name': service_name,
            'total_reviews': 0,
            'average_rating': 0,
            'rating_breakdown': {str(i): 0 for i in range(1, 6)}
        })
    
    stats = reviews.aggregate(
        total=Count('id'),
        avg_rating=Avg('rating')
    )
    
    rating_breakdown = {}
    for i in range(1, 6):
        rating_breakdown[str(i)] = reviews.filter(rating=i).count()
    
    return Response({
        'service_name': service_name,
        'total_reviews': stats['total'],
        'average_rating': round(stats['avg_rating'], 1),
        'rating_breakdown': rating_breakdown,
        'recent_reviews': ReviewSerializer(
            reviews.order_by('-created_at')[:3], 
            many=True,
            context={'request': request}
        ).data
    })

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def quick_review(request):
    """Quick review endpoint for simple rating submissions"""
    service_name = request.data.get('service_name')
    rating = request.data.get('rating')
    comment = request.data.get('comment', '')
    
    if not service_name or not rating:
        return Response({
            'error': 'service_name and rating are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user already reviewed this service
    existing_review = Review.objects.filter(
        user=request.user,
        service_name=service_name
    ).first()
    
    if existing_review:
        return Response({
            'error': 'You have already reviewed this service',
            'existing_review_id': existing_review.id
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        rating = int(rating)
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
    except (ValueError, TypeError):
        return Response({
            'error': 'Invalid rating. Must be an integer between 1 and 5'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    review = Review.objects.create(
        user=request.user,
        service_name=service_name,
        rating=rating,
        comment=comment
    )
    
    return Response({
        'message': 'Review submitted successfully',
        'review': ReviewSerializer(review, context={'request': request}).data
    }, status=status.HTTP_201_CREATED)