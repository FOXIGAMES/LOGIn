from django.db.models import Avg
from rest_framework import serializers
from impressions.models import Rating, Comment, Like
from myzloo.models import MusicTrack
from rest_framework.response import Response


class RatingSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    title = serializers.ReadOnlyField(source='track.title')
    track = serializers.ReadOnlyField(source='track.id')

    class Meta:
        model = Rating
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['rating'] = instance.ratings.aggregate(
            Avg('rating')
        )
        rating = representation['rating']
        rating['rating_count'] = instance.ratings.count()
        return representation

    def create(self, validated_data):
        track = self.context.get('track')
        owner = self.context.get('owner')
        validated_data['track'] = track
        validated_data['owner'] = owner
        return super().create(validated_data)

    def validate(self, attrs):
        rating = attrs.get('rating')
        if not rating:
            return serializers.ValidationError('Rating was not handed')
        if int(rating) not in range(1, 6):
            return serializers.ValidationError('Rating should be from 1 to 5')
        return attrs




class RatedSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source='owner.email')
    track_title = serializers.ReadOnlyField(source='track.title')


    class Meta:
        model = Rating
        fields = ['owner_email', 'track_title', 'rating']



class CommentSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    owner_email = serializers.ReadOnlyField(source='owner.email')
    track = serializers.ReadOnlyField(source='track.id')
    track_title = serializers.ReadOnlyField(source='track.title')

    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        track = self.context.get('file')
        track = MusicTrack.objects.get(audio_file=track.audio_file)
        owner = self.context.get('author')
        validated_data['owner'] = owner
        validated_data['track'] = track
        return super().create(validated_data)


class CommentListSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Comment
        fields = ['owner_email', 'content', 'created_at']


class LikeSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Like
        fields = '__all__'

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        track = attrs['track']
        if user.likes.filter(trac=track).exists():
            return Response('You already liked this video', status=400)
        return attrs


class LikedUserSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source='owner.email')
    track_title = serializers.ReadOnlyField(source='track.title')

    class Meta:
        model = Like
        fields = ('owner_email', 'track_title')