from django.urls import path
from . import views
# from .views import search_picture, #CustomUserDetailView, CustomTokenObtainPairView
from .views import search_picture, CustomUserByUsernameView, CustomTokenObtainPairView

urlpatterns = [
    path('avatars/<str:email>/', search_picture, name='avatars'),
    path('api/user/', CustomUserByUsernameView.as_view(), name='user-detail'),

    path('filter/', views.FilterByArtistViewSet.as_view({'get': 'list'}), name='filter-by-artist'),
    path('search/', views.SearchByTitleViewSet.as_view({'get': 'list'}), name='search-by-title'),
    path('genres/', views.GenreAPIView.as_view({'get': 'list'}), name='track_genre'),
    path('filter_by_genres/', views.FilterByGenreViewSet.as_view({'get': 'list'}), name='filter-by-genre'),
]