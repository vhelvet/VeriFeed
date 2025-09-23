from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

router = DefaultRouter()
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    path('reviews/<int:review_id>/helpful/', 
         views.ReviewHelpfulToggleView.as_view(), 
         name='review-helpful-toggle'),
    path('services/<str:service_name>/reviews/', 
         views.ServiceReviewsView.as_view(), 
         name='service-reviews'),
    path('services/<str:service_name>/summary/', 
         api_views.service_review_summary, 
         name='service-review-summary'),
    path('users/<int:user_id>/reviews/', 
         views.UserReviewsView.as_view(), 
         name='user-reviews'),
    path('user/stats/', 
         api_views.user_review_stats, 
         name='user-review-stats'),
    path('quick-review/', 
         api_views.quick_review, 
         name='quick-review'),
    
    # Web interface (optional)
    path('web/', views.ReviewListView.as_view(), name='review-list-page'),
    path('web/add/', views.AddReviewView.as_view(), name='add-review'),
]