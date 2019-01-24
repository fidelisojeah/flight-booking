from django.urls import path
from rest_framework.routers import DefaultRouter


from . import views

urlpatterns = [
]

router = DefaultRouter()
router.register(r'reservations', views.ReservationViewSet,
                basename='reservations')
router.register(r'flights', views.FlightsViewSet,
                basename='flights')
router.register(r'airlines', views.AirlineViewSet,
                basename='airlines')

router.register(r'accounts', views.AccountReservationViewSet,
                basename='account-reservations')


urlpatterns += router.urls
