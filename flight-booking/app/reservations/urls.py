from django.urls import path
from rest_framework.routers import DefaultRouter


from . import views

urlpatterns = [
]

router = DefaultRouter()
router.register(r'reservations', views.ReservationViewSet,
                basename='reservations')
router.register(r'reservations/flights', views.FlightsViewSet,
                basename='flights')

urlpatterns += router.urls
