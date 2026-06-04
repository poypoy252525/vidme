from django.urls import path, include
from rest_framework.routers import  DefaultRouter

from video.views import VideoViewSet

router = DefaultRouter()

router.register('video', VideoViewSet, basename='video')

urlpatterns = [
    path('', include(router.urls))
]