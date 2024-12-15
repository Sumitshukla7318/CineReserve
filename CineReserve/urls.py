from django.urls import path
from BookingApk.views import TheaterAvailabilityView, CustomUnavailabilityView, AvailableSlotsView
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/theatre/<int:id>/availability/', TheaterAvailabilityView.as_view(), name='theater-availability'),
    path('api/theatre/<int:id>/custom-unavailability/', CustomUnavailabilityView.as_view(), name='custom-unavailability'),
    path('api/theatre/<int:id>/slots/', AvailableSlotsView.as_view(), name='available-slots'),
]
