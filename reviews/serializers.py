from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Review, ReviewHelpful

User = get_user_model()

class ReviewUserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture_url', 'full_name']
    
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)
    stars_display = serializers.ReadOnlyField()
    user_has_voted_helpful = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'service_name', 'user', 'rating', 'title', 'comment',
            'created_at', 'updated_at', 'is_verified', 'helpful_count',
            'stars_display', 'user_has_voted_helpful'
        ]
        read_only_fields = ['user', 'helpful_count', 'is_verified']
    
    def get_user_has_voted_helpful(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ReviewHelpful.objects.filter(
                review=obj, user=request.user
            ).exists()
        return False
    
    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate(self, data):
        request = self.context.get('request')
        if request and request.method == 'POST':
            # Check if user already reviewed this service
            if Review.objects.filter(
                service_name=data['service_name'],
                user=request.user
            ).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this service."
                )
        return data