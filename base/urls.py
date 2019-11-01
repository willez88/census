from django.urls import path
from .views import HomeView, Error403View

app_name = 'base'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('error-403/', Error403View.as_view(), name = 'error_403'),
]
