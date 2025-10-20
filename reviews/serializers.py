from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Review, ReviewHelpful, Feedback

User = get_user_model()

class ReviewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "profile_picture"]


class ReviewSimpleSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.username", read_only=True)
    user_picture = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "service_name",
            "rating",
            "title",
            "comment",
            "created_at",
            "user_name",
            "user_picture",
        ]

    def get_user_picture(self, obj):
        request = self.context.get("request")
        if obj.user and getattr(obj.user, "profile_picture", None):
            url = obj.user.profile_picture.url
            return request.build_absolute_uri(url) if request else url
        return None


class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)
    stars_display = serializers.ReadOnlyField()
    user_has_voted_helpful = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'service_name', 'rating', 'comment', 'created_at']
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
            if Review.objects.filter(
                service_name=data['service_name'],
                user=request.user
            ).exists():
                raise serializers.ValidationError(
                    "You have already reviewed this service."
                )
        return data


class FeedbackSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'user', 'message', 'created_at']
        read_only_fields = ['user', 'created_at']
