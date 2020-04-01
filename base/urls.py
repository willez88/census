from django.urls import path, re_path
from .views import HomeView, Error403View, ExportExcelView
from .ajax import ComboUpdateView
from django.contrib.auth.decorators import login_required

app_name = 'base'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('error-403/', Error403View.as_view(), name = 'error_403'),
    path('descargar-archivo/', ExportExcelView.as_view(), name = 'export_excel'),

    re_path(r'^ajax/combo-update/?$', login_required(ComboUpdateView.as_view()), name='combo_update'),
]
