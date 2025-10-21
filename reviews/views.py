from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication  # ✅ CONSISTENT JWT AUTH
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Avg, Count
from .models import Review, ReviewHelpful, Feedback
from .serializers import ReviewSerializer, FeedbackSerializer, ReviewSimpleSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().select_related('user')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [JWTAuthentication]  # ✅ CONSISTENT JWT AUTH

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {'error': 'You can only edit your own reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            return Response(
                {'error': 'You can only delete your own reviews.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get current user's reviews"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'},
                          status=status.HTTP_401_UNAUTHORIZED)
        reviews = Review.objects.filter(user=request.user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

class ServiceReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        service_name = self.kwargs['service_name']
        return Review.objects.filter(service_name=service_name).select_related('user')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        stats = queryset.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id'),
        )
        rating_breakdown = {}
        for i in range(1, 6):
            rating_breakdown[f'{i}_star'] = queryset.filter(rating=i).count()
        
        return Response({
            'reviews': serializer.data,
            'statistics': {
                'average_rating': round(stats['avg_rating'] or 0, 1),
                'total_reviews': stats['total_reviews'],
                'rating_breakdown': rating_breakdown
            }
        })

class UserReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Review.objects.filter(user_id=user_id).select_related('user')

class ReviewHelpfulToggleView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]  

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        helpful_vote, created = ReviewHelpful.objects.get_or_create(
            review=review,
            user=request.user
        )
        if created:
            review.helpful_count += 1
            review.save()
            return Response({
                'helpful': True,
                'helpful_count': review.helpful_count
            })
        else:
            helpful_vote.delete()
            review.helpful_count = max(0, review.helpful_count - 1)
            review.save()
            return Response({
                'helpful': False,
                'helpful_count': review.helpful_count
            })

# Django Template Views (Optional - for web interface)
class ReviewListView(ListView):
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        return Review.objects.all().select_related('user').order_by('-created_at')

class QuickReviewView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]  

    def get(self, request):
        """GET method for testing"""
        return Response({
            "message": "QuickReviewView GET works", 
            "user": str(request.user),
            "authenticated": request.user.is_authenticated
        })

    def post(self, request):
        """POST method for submitting reviews"""
        print(f"🔍 QuickReviewView POST called by user: {request.user}")
        print(f"🔍 User authenticated: {request.user.is_authenticated}")
        print(f"🔍 Request data: {request.data}")
        print(f"🔍 Request headers: {request.META.get('HTTP_AUTHORIZATION', 'No auth header')}")
        
        try:
            # Enhanced data handling for different input formats
            data = request.data.copy()
            
            # Handle different field names from frontend
            if 'message' in data and not data.get('comment'):
                data['comment'] = data['message']
            
            # Ensure required fields
            if not data.get('service_name'):
                data['service_name'] = 'General'
            
            # Validate required fields
            if not data.get('rating'):
                return Response({
                    'error': 'Rating is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not data.get('comment'):
                return Response({
                    'error': 'Comment is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = ReviewSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                review = serializer.save(user=request.user)
                return Response({
                    'message': 'Review submitted successfully',
                    'review': ReviewSerializer(review, context={'request': request}).data
                }, status=status.HTTP_201_CREATED)
            else:
                print(f"🔴 Serializer errors: {serializer.errors}")
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"🔴 Exception in QuickReviewView: {str(e)}")
            return Response({
                'error': 'Internal server error',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(login_required, name='dispatch')
class AddReviewView(CreateView):
    model = Review
    fields = ['service_name', 'rating', 'title', 'comment']
    template_name = 'reviews/add_review.html'
    success_url = reverse_lazy('review-list-page')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Your review has been added successfully!')
        return super().form_valid(form)

# Consistent authentication for feedback
@api_view(['GET', 'POST'])
def submit_feedback(request):
    if request.method == 'GET':
        # GET is public - anyone can view feedback
        qs = Feedback.objects.select_related('user').order_by('-created_at')
        serializer = FeedbackSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)
    
    if request.method == 'POST':
        # POST requires authentication
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required to submit feedback"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([JWTAuthentication]) 
@permission_classes([IsAuthenticated])
def quick_review(request):
    """Main quick review endpoint - matches frontend API call"""
    print(f"🔍 quick_review called by: {request.user}")
    print(f"🔍 Authenticated: {request.user.is_authenticated}")
    print(f"🔍 Data: {request.data}")
    
    try:
        data = request.data.copy()
        
        # Handle field mapping
        if 'message' in data and not data.get('comment'):
            data['comment'] = data['message']
        
        if not data.get('service_name'):
            data['service_name'] = 'General'
        
        # Create review directly 
        review = Review.objects.create(
            user=request.user,
            service_name=data.get('service_name', 'General'),
            rating=int(data.get('rating', 5)),
            comment=data.get('comment', ''),
            title=data.get('title', '')
        )
        
        return Response({
            'message': 'Review submitted successfully',
            'review': {
                'id': review.id,
                'service_name': review.service_name,
                'rating': review.rating,
                'comment': review.comment,
                'user': request.user.username,
                'created_at': review.created_at
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"🔴 Error in quick_review: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
@permission_classes([AllowAny])
def service_review_summary(request, service_name):
    """Public endpoint for service review summaries"""
    reviews = Review.objects.filter(service_name=service_name).select_related('user')
    
    stats = reviews.aggregate(
        avg_rating=Avg("rating"),
        total_reviews=Count("id"),
    )
    
    rating_breakdown = {str(i): reviews.filter(rating=i).count() for i in range(1, 6)}
    
    recent = reviews.order_by('-created_at')[:20]
    
    return Response({
        "service_name": service_name,
        "average_rating": round(stats["avg_rating"] or 0, 1),
        "total_reviews": stats["total_reviews"],
        "rating_breakdown": rating_breakdown,
        "recent_reviews": ReviewSimpleSerializer(recent, many=True, context={'request': request}).data,
    })

@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def test_endpoint(request):
    """Test endpoint to debug authentication"""
    return Response({
        "message": f"{request.method} request received",
        "user": str(request.user) if request.user.is_authenticated else "Anonymous",
        "authenticated": request.user.is_authenticated,
        "auth_header": request.META.get('HTTP_AUTHORIZATION', 'No auth header'),
        "data": request.data if request.method == 'POST' else None
    })