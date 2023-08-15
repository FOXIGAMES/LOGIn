from django.http import HttpResponse, Http404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import CustomUser, myzloo_favorites, Genre
from rest_framework import generics, status, permissions
from .models import MusicTrack
from .serializers import MusicTrackSerializer, GenreSerializer, FilterTrackSerializer, FilterTrackByGenreSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import RegisterSerializer, CustomUserSerializer
from .send_email import send_confirmation_email
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from rest_framework import request

User = get_user_model()


class StandartResultPagination(PageNumberPagination):
    page_size = 4
    page_query_param = 'page'

class GenreAPIView(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return (permissions.IsAuthorOrAdmin(),)
        elif self.request.method in ['PUT', 'PATCH']:
            return (permissions.IsAuthorOrAdmin(),)
        return (permissions.AllowAny(),)

class MusicTrackListCreateView(generics.ListCreateAPIView):
    queryset = MusicTrack.objects.all()
    serializer_class = MusicTrackSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAdminUser()]

class MusicTrackDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MusicTrack.objects.all()
    serializer_class = MusicTrackSerializer
    permission_classes = [IsAdminUser | IsAuthenticatedOrReadOnly]

class CustomUserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        user = self.get_object()
        track_id = request.data.get('track_id')

        try:
            track = MusicTrack.objects.get(pk=track_id)
            if track in user.favorites.all():
                user.favorites.remove(track)
                return Response({"message": "Track removed from favorites"}, status=status.HTTP_200_OK)
            else:
                user.favorites.add(track)
                return Response({"message": "Track added to favorites"}, status=status.HTTP_200_OK)
        except MusicTrack.DoesNotExist:
            return Response({"error": "Track not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomUserByUsernameView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)

        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

class AddRemoveFavoriteView(generics.GenericAPIView):
    queryset = MusicTrack.objects.all()
    serializer_class = MusicTrackSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, pk):
        user = request.user

        try:
            track = MusicTrack.objects.get(pk=pk)
            favorite, created = myzloo_favorites.objects.get_or_create(user=user, track=track)

            if created:
                return Response({'message': 'Added to favorites'}, status=status.HTTP_201_CREATED)
            else:
                favorite.delete()
                return Response({'message': 'Removed from favorites'}, status=status.HTTP_200_OK)
        except MusicTrack.DoesNotExist:
            return Response({'message': 'Music track not found'}, status=status.HTTP_404_NOT_FOUND)


class RegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            try:
                send_confirmation_email(user.email, 'http://16.171.145.163/api/account/activate/?u='+str(user.activation_code))
            except:
                return Response({'message': 'Зарегистрирован, но не смог отправить код активации',
                                 'data': serializer.data}, status=201)

        return Response(serializer.data, status=201)


class ActivationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('u')
        user = get_object_or_404(User, activation_code=code)

        if user.is_active:
            return Response({"message": "Учетная запись уже активирована"}, status=400)

        user.is_active = True
        user.activation_code = ''
        user.save()

        return Response({"message": "Успешно активирован"}, status=200)




class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = permissions.IsAuthenticated,

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response('You logged out', status=205)
        except:
            return Response('Smth went wrong', status=400)

class FilterByArtistViewSet(viewsets.ModelViewSet):
    queryset = MusicTrack.objects.all()
    serializer_class = FilterTrackSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        artist_filter = self.request.query_params.get('artist')
        if artist_filter:
            queryset = queryset.filter(artist__icontains=artist_filter)
        return queryset


class FilterByGenreViewSet(viewsets.ModelViewSet):
    queryset = MusicTrack.objects.all()
    serializer_class = FilterTrackByGenreSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        genre_filter = self.request.query_params.get('genre')
        if genre_filter:
            queryset = queryset.filter(genre__genre__iexact=genre_filter)
        return queryset


class SearchByTitleViewSet(viewsets.ModelViewSet):
    queryset = MusicTrack.objects.all()
    serializer_class = FilterTrackSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        title_search = self.request.query_params.get('title')
        print("Title search:", title_search)
        if title_search:
            queryset = queryset.filter(title__icontains=title_search)
        return queryset

def send_daily_notification_to_users():
    users = User.objects.filter(is_active=True)
    subject = 'Ежедневное уведомление от сайта музыки'
    message = 'Привет! Это ваше ежедневное уведомление от сайта музыки.'
    from_email = 'akusevtimur733@gmail.com'

    for user in users:
        send_mail(subject, message, from_email, [user.email])



from rest_framework.viewsets import ModelViewSet
from myzloo.models import MusicTrack
from rest_framework import permissions
from rest_framework.decorators import action
from myzloo.serializers import *
from myzloo.permissions import IsAdminOrReadOnly, IsAuthenticatedOrCreateOnly
from rest_framework.response import Response
from impressions.serializers import CommentSerializer, LikedUserSerializer, RatedSerializer, RatingSerializer, \
    CommentListSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from impressions.models import Like, Rating




class StandartResultPagination(PageNumberPagination):
    page_size = 5
    page_query_param = 'page'


class TrackViewSet(ModelViewSet):
    queryset = MusicTrack.objects.all()
    pagination_class = StandartResultPagination
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('title', 'artist')
    filterset_fields = ('title', 'artist')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['list']:
            return MusicTrackSerializer
        return TrackDetailSerializer

    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return IsAdminOrReadOnly(),
        return permissions.IsAuthenticatedOrReadOnly(),

    @action(methods=['GET', 'POST', 'DELETE'], detail=True)
    def comments(self, request, pk):
        track = self.get_object()
        user = request.user
        if request.method == 'GET':
            comments = track.comments.all()
            serializer = CommentListSerializer(instance=comments, many=True)
            return Response(serializer.data, status=200)

        elif request.method == 'POST':
            serializer = CommentSerializer(data=request.data, context={'file': track, 'author': user})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=201)

        elif request.method == 'DELETE':
            comment_id = self.request.query_params.get('id')
            comment = track.comments.filter(track=track, pk=comment_id)

            if comment.exists():
                comment.delete()
                return Response('Successfully deleted', status=204)
        return Response('Not found', status=404)

    @action(methods=['POST', 'GET'], detail=True)
    def likes(self, request, pk):
        track = self.get_object()
        user = request.user
        if request.method == 'GET':
            likes = track.likes.all()
            serializer = LikedUserSerializer(instance=likes, many=True)
            return Response(serializer.data, status=200)

        elif request.method == 'POST':
            if user.likes.filter(track=track).exists():
                user.likes.filter(track=track).delete()
                return Response('Like was deleted', status=204)
            Like.objects.create(owner=user, track=track)
            return Response('Like has been added', status=201)


    @action(methods=['GET', 'POST', 'PUT', 'DELETE'],detail =True)
    def rating(self, request, pk):
        track = self.get_object()
        user = request.user

        if request.method == 'GET':
            ratings = track.ratings.all()
            serializer = RatedSerializer(instance=ratings, many=True)
            return Response(serializer.data, status=200)

        elif request.method == 'POST':
            if user.ratings.filter(track=track).exists():
                return Response('You already rated this track')

            serializator = RatingSerializer(data=request.data, context={'track': track, 'owner': user})
            serializator.is_valid(raise_exception=True)
            serializator.save()
            return Response('Rating was added', status=201)

        elif request.method == 'PUT':
            user_rating = user.ratings.filter(track=track).first()
            if user_rating:
                serializer = RatedSerializer(user_rating, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=400)

        elif request.method == 'DELETE':
            if user.ratings.filter(track=track).exists():
                user.ratings.filter(track=track).delete()
                return Response('Rating was deleted', status=204)
        return Response({'error': 'Rating not found.'}, status=404)



def search_picture(request, email):
    user = get_object_or_404(CustomUser, email=email)

    if user.avatar:
        image_data = open(user.avatar.path, "rb").read()
        return HttpResponse(image_data, content_type="image/jpeg")
    else:
        raise Http404