from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'accounts', views.UserAuthViewSet, basename='accounts')

urlpatterns = router.urls
