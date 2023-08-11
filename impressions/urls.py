from django.urls import path, include
from myzloo.views import TrackViewSet
from rest_framework.routers import DefaultRouter




router = DefaultRouter()
router.register(r'tracks', TrackViewSet)

urlpatterns = [
    path('', include(router.urls)),
]