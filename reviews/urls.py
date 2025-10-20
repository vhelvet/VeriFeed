from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views, api_views

router = DefaultRouter()
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    
    # Review-related endpoints
    path('reviews/<int:review_id>/helpful/', 
         views.ReviewHelpfulToggleView.as_view(), name='review-helpful-toggle'),
    path('services/<str:service_name>/reviews/', 
         views.ServiceReviewsView.as_view(), name='service-reviews'),
    path('services/<str:service_name>/summary/', 
         api_views.service_review_summary, name='service-review-summary'),
    path('users/<int:user_id>/reviews/', 
         views.UserReviewsView.as_view(), name='user-reviews'),
    path('user/stats/', 
         api_views.user_review_stats, name='user-review-stats'),
    
    # MAIN FEEDBACK/REVIEW ENDPOINTS (frontend calls)
    path('quick-review/', views.quick_review, name='quick-review-main'),
    path('reviews/quick-review/', views.QuickReviewView.as_view(), name='quick-review-class'),
    
    # PUBLIC ENDPOINT (review summaries)
    path("service_review_summary/<str:service_name>/", 
         views.service_review_summary, name="service_review_summary"),
    
    # FEEDBACK ENDPOINT
    path('feedback/', views.submit_feedback, name='submit-feedback'),
    
    # Web interface
    path('web/', views.ReviewListView.as_view(), name='review-list-page'),
    path('web/add/', views.AddReviewView.as_view(), name='add-review'),
    
    # User profiles
    path('profile/<int:user_id>/', views.UserReviewsView.as_view(), name='user_profile'),
    
    # TEST ENDPOINT (for debugging)
    path('test-endpoint/', views.test_endpoint, name='test-endpoint'),
]