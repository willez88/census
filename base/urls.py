from django.contrib.auth.decorators import login_required
from django.urls import path

from .ajax import ComboUpdateView
from .views import (
    BuildingListView,
    DemographicCensusTemplateView,
    DepartmentListView,
    Error403View,
    ExportExcelStreetLeaderView,
    ExportExcelView,
    GenderListView,
    GetDepartmentView,
    HomeView,
    RelationshipListView,
    VoterTemplateView,
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
        'descargar-archivo-lider-calle/',
        login_required(ExportExcelStreetLeaderView.as_view()),
        name='export_excel_street_leader'
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
        'buildings/list/', login_required(BuildingListView.as_view()),
        name='building_list'
    ),
    path(
        'departments/list/', login_required(DepartmentListView.as_view()),
        name='department_list'
    ),
    path(
        'get-departments/<int:building_id>/',
        login_required(GetDepartmentView.as_view()),
        name='get-departments'
    ),
    path(
        'genders/list/', login_required(GenderListView.as_view()),
        name='gender_list'
    ),
    path(
        'descargar-votantes/',
        login_required(VoterTemplateView.as_view()),
        name='voter'
    ),
    path(
        'descargar-censo-demografico/',
        login_required(DemographicCensusTemplateView.as_view()),
        name='demographic_census'
    ),

    path(
        'ajax/combo-update/', login_required(ComboUpdateView.as_view()),
        name='combo_update'
    ),
]
