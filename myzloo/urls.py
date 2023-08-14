from django.urls import path
from . import views
# from .views import search_picture, #CustomUserDetailView, CustomTokenObtainPairView
from .views import search_picture, CustomUserByUsernameView, CustomTokenObtainPairView

urlpatterns = [
    # path('filter/', views.FilterByArtistViewSet.as_view({'get': 'list'}), name='filter-by-artist'),
    # path('search/', views.SearchByTitleViewSet.as_view({'get': 'list'}), name='search-by-title'),
    # path('search_name/', views.SearchByFirstNameViewSet.as_view({'get': 'list'}), name='search_by_name'),
    path('avatars/<str:email>/', search_picture, name='avatars'),
    # path('login_profile/', views.LoginView.as_view()),
    # path('api/user/', CustomUserDetailView.as_view(), name='user-detail'),
    # path('api/token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('api/user/', CustomUserByUsernameView.as_view(), name='user-detail'),
    # path('api/token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),#not worked
]