from django.contrib.auth.decorators import login_required
from django.urls import path

from .ajax import ComboUpdateView
from .views import (
    Error403View, ExportExcelView, HomeView, RelationshipListView,
    VoteTypeListView,
)

app_name = 'base'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('error-403/', Error403View.as_view(), name='error_403'),
    path(
        'descargar-archivo/', login_required(ExportExcelView.as_view()),
        name='export_excel'
    ),
    path(
        'vote-types/list/', login_required(VoteTypeListView.as_view()),
        name='vote_type_list'
    ),
    path(
        'relationships/list/', login_required(RelationshipListView.as_view()),
        name='relationship_list'
    ),

    path(
        'ajax/combo-update/', login_required(ComboUpdateView.as_view()),
        name='combo_update'
    ),
]
