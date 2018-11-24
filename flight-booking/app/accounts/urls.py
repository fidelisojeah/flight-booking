from django.urls import path
from rest_framework.routers import DefaultRouter

from rest_framework_jwt.views import refresh_jwt_token

from . import views

urlpatterns = [
    path('accounts/refresh/', refresh_jwt_token),
]

router = DefaultRouter()
router.register(r'accounts', views.UserAuthViewSet, basename='accounts')

urlpatterns += router.urls
