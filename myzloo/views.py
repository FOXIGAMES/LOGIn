from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import CustomUser, myzloo_favorites
from rest_framework import generics, status, permissions
from .models import MusicTrack
from .serializers import MusicTrackSerializer
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

User = get_user_model()

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
                send_confirmation_email(user.email, 'http://127.0.0.1:3000/api/account/activate/?u='+str(user.activation_code))
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


def send_daily_notification_to_users():
    users = User.objects.filter(is_active=True)
    subject = 'Ежедневное уведомление от сайта музыки'
    message = 'Привет! Это ваше ежедневное уведомление от сайта музыки.'
    from_email = 'akusevtimur733@gmail.com'

    for user in users:
        send_mail(subject, message, from_email, [user.email])
