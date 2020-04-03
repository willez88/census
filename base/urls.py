from django.urls import path, re_path
from .views import HomeView, Error403View, ExportExcelView, VoteTypeListView, RelationshipListView
from .ajax import ComboUpdateView
from django.contrib.auth.decorators import login_required

app_name = 'base'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('error-403/', Error403View.as_view(), name = 'error_403'),
    path('descargar-archivo/', login_required(ExportExcelView.as_view()), name = 'export_excel'),
    path('vote-types/list/', login_required(VoteTypeListView.as_view()), name='vote_type_list'),
    path('relationships/list/', login_required(RelationshipListView.as_view()), name='relationship_list'),

    re_path(r'^ajax/combo-update/?$', login_required(ComboUpdateView.as_view()), name='combo_update'),
]
