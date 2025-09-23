from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Avg, Count
from .models import Review, ReviewHelpful
from .serializers import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().select_related('user')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]
    
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
        
        # Add summary statistics
        stats = queryset.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id'),
            rating_breakdown=Count('rating')
        )
        
        # Rating breakdown
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
    authentication_classes = [TokenAuthentication]
    
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        
        helpful_vote, created = ReviewHelpful.objects.get_or_create(
            review=review,
            user=request.user
        )
        
        if created:
            # User marked as helpful
            review.helpful_count += 1
            review.save()
            return Response({
                'helpful': True, 
                'helpful_count': review.helpful_count
            })
        else:
            # User removed helpful vote
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