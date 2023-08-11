# from rest_framework.viewsets import ModelViewSet
# from myzloo.models import MusicTrack
# from rest_framework import permissions
# from rest_framework.decorators import action
# from myzloo.serializers import *
# from myzloo.permissions import IsAdminOrReadOnly, IsAuthenticatedOrCreateOnly
# from rest_framework.response import Response
# from impressions.serializers import CommentSerializer, LikedUserSerializer,  RatedSerializer, RatingSerializer
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.filters import SearchFilter
# from django_filters.rest_framework import DjangoFilterBackend
# from impressions.models import Like, Rating
#
#
#
#
# class StandartResultPagination(PageNumberPagination):
#     page_size = 5
#     page_query_param = 'page'
#
#
# class TrackViewSet(ModelViewSet):
#     queryset = MusicTrack.objects.all()
#     pagination_class = StandartResultPagination
#     filter_backends = (SearchFilter, DjangoFilterBackend)
#     search_fields = ('title', 'artist')
#     filterset_fields = ('title', 'artist')
#
#     def perform_create(self, serializer):
#         serializer.save(author=self.request.user)
#
#     def get_serializer_class(self):
#         if self.action in ['list']:
#             return MusicTrackSerializer
#         return TrackDetailSerializer
#
#     def get_permissions(self):
#         if self.action in ['destroy', 'update', 'partial_update']:
#             return IsAdminOrReadOnly(),
#         return permissions.IsAuthenticatedOrReadOnly(),
#
#     @action(methods=['GET', 'POST', 'DELETE'], detail=True)
#     def comments(self, request, pk):
#         track = self.get_object()
#         user = request.user
#         if request.method == 'GET':
#             comments = track.comments.all()
#             serializer = CommentSerializer(instance=comments, many=True)
#             return Response(serializer.data, status=200)
#
#         elif request.method == 'POST':
#             serializer = CommentSerializer(data=request.data, context={'file': track, 'author': user})
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response(serializer.data, status=201)
#
#         elif request.method == 'DELETE':
#             comment_id = self.request.query_params.get('id')
#             comment = track.comments.filter(track=track, pk=comment_id)
#             print(dir(comment))
#             if comment.exists():
#                 comment.delete()
#                 return Response('Successfully deleted', status=204)
#         return Response('Not found', status=404)
#
#     @action(methods=['POST', 'GET'], detail=True)
#     def likes(self, request, pk):
#         track = self.get_object()
#         user = request.user
#         if request.method == 'GET':
#             likes = track.likes.all()
#             serializer = LikedUserSerializer(instance=likes, many=True)
#             return Response(serializer.data, status=200)
#
#         elif request.method == 'POST':
#             if user.likes.filter(track=track).exists():
#                 user.likes.filter(track=track).delete()
#                 return Response('Like was deleted', status=204)
#             Like.objects.create(owner=user, track=track)
#             return Response('Like has been added', status=201)
#
#     @action(methods=['POST', 'GET'], detail=True)
#     def favorites(self, request, pk):
#         track = self.get_object()
#         user = request.user
#         if request.method == 'GET':
#             favorites = track.favorites.all()
#             serializer = FavoriteSerializer(instance=favorites, many=True)
#             return Response(serializer.data, status=200)
#
#         elif request.method == 'POST':
#             if user.favorites.filter(track=track).exists():
#                 user.favorites.filter(track=track).delete()
#                 return Response('Track was deleted from favorites', status=204)
#             Favorite.objects.create(owner=user, track=track)
#             return Response('Track has been added to favorites', status=201)
#
#     @action(methods=['GET', 'POST', 'PUT', 'DELETE'], detail=True)
#     def rating(self, request, pk):
#         track = self.get_object()
#         user = request.user
#
#         if request.method == 'GET':
#             ratings = track.ratings.all()
#             serializer = RatedSerializer(instance=ratings, many=True)
#             return Response(serializer.data, status=200)
#
#         elif request.method == 'POST':
#             if user.ratings.filter(track=track).exists():
#                 return Response('You already rated this track')
#
#             serializator = RatingSerializer(data=request.data, context={'track': track, 'owner': user})
#             serializator.is_valid(raise_exception=True)
#             serializator.save()
#             return Response('Rating was added', status=201)
#
#         elif request.method == 'PUT':
#             user_rating = user.ratings.filter(track=track).first()
#             if user_rating:
#                 serializer = RatedSerializer(user_rating, data=request.data)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response(serializer.data)
#                 return Response(serializer.errors, status=400)
#
#         elif request.method == 'DELETE':
#             if user.ratings.filter(track=track).exists():
#                 user.ratings.filter(track=track).delete()
#                 return Response('Rating was deleted', status=204)
#         return Response({'error': 'Rating not found.'}, status=404)
#
#
#
#
#
# from rest_framework import permissions, generics
# from myzloo.models import MusicTrack
# from myzloo.serializers import TrackDetailSerializer
# from django.db.models import Avg
#
#
# class RecommendationView(generics.ListAPIView):
#     queryset = MusicTrack.objects.annotate(average_rating=Avg('ratings__rating')).order_by('-average_rating')
#     serializer_class = TrackDetailSerializer
#     permission_classes = permissions.AllowAny,