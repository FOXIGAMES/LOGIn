from django.db import models
from django.contrib.auth import get_user_model
from myzloo.models import MusicTrack

User = get_user_model()


class Comment(models.Model):
    owner = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    track = models.ForeignKey(MusicTrack, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    attachment = models.FileField(upload_to=f'{track}/files', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'User: {self.owner}  track: {self.track}    comment: {self.content}'


class Rating(models.Model):
    RATING_CHOICES = (
        (1, 'Too bad'),
        (2, 'Bad'),
        (3, 'Normal'),
        (4, 'Good'),
        (5, 'Excellent')
    )
    track = models.ForeignKey(MusicTrack, related_name='ratings', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name='ratings', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['owner', 'track']

    def __str__(self):
        return f'Track: {self.track} with rating: {self.rating}'


class Like(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    track = models.ForeignKey(MusicTrack, on_delete=models.CASCADE, related_name='likes')

    def __str__(self):
        return f'{self.owner.email} -> {self.track.title}'