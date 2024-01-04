from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy

from .views import (
    AdmonitionCreateView,
    AdmonitionDeleteView,
    AdmonitionListView,
    AdmonitionUpdateView,
    CensusListView,
    CondominiumCreateView,
    CondominiumDetailView,
    CondominiumListView,
    CommunityLeaderFormView,
    CommunityLeaderListView,
    FamilyDetailView,
    FamilyGroupCreateTemplateView,
    FamilyGroupDetailView,
    FamilyGroupEditTemplateView,
    FamilyGroupListView,
    FamilyGroupSaveView,
    FamilyGroupUpdateView,
    MoveOutCreateView,
    MoveOutListView,
    MoveOutUpdateView,
    PersonDeleteView,
    ProfileUpdateView,
    SearchForAgeView,
    SearchView,
    StreetLeaderFormView,
    StreetLeaderListView,
)

app_name = 'user'

urlpatterns = [
    path(
        'login/', views.LoginView.as_view(template_name='user/login.html'),
        name='login'
    ),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path(
        'reset/password-reset/',
        views.PasswordResetView.as_view(
            template_name='user/password_reset_form.html',
            email_template_name='user/password_reset_email.html',
            success_url=reverse_lazy('user:password_reset_done')
        ),
        name='password_reset'
    ),
    path(
        'password-reset-done/',
        views.PasswordResetDoneView.as_view(
            template_name='user/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        views.PasswordResetConfirmView.as_view(
            template_name='user/password_reset_confirm.html',
            success_url=reverse_lazy('user:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        views.PasswordResetCompleteView.as_view(
            template_name='user/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
    path(
        'password-change/',
        login_required(views.PasswordChangeView.as_view(
            template_name='user/password_change_form.html',
            success_url=reverse_lazy('user:password_change_done')
        )),
        name='password_change'
    ),
    path(
        'password-change-done/',
        login_required(views.PasswordChangeDoneView.as_view(
            template_name='user/password_change_done.html'
        )),
        name='password_change_done'
    ),

    path(
        'profile/update/<int:pk>/',
        login_required(ProfileUpdateView.as_view()),
        name='profile_update'
    ),
    path(
        'community-leader/list/',
        login_required(CommunityLeaderListView.as_view()),
        name='community_leader_list'
    ),
    path(
        'community-leader/create/',
        login_required(CommunityLeaderFormView.as_view()),
        name='community_leader_create'
    ),
    path(
        'street-leader/list/',
        login_required(StreetLeaderListView.as_view()),
        name='street_leader_list'
    ),
    path(
        'street-leader/create/',
        login_required(StreetLeaderFormView.as_view()),
        name='street_leader_create'
    ),
    path(
        'family-group/list/',
        login_required(FamilyGroupListView.as_view()),
        name='family_group_list'
    ),
    # path(
    #   'family_group/create/', login_required(FamilyGroupFormView.as_view()),
    #   name='family_group_create'
    # ),

    path(
        'family-group/create/',
        login_required(FamilyGroupCreateTemplateView.as_view()),
        name='family_group_create'
    ),
    path(
        'family-group/save/',
        login_required(FamilyGroupSaveView.as_view()),
        name='family_group_save'
    ),

    path(
        'family-group/edit/<int:pk>/',
        login_required(FamilyGroupEditTemplateView.as_view()),
        name='family_group_edit'
    ),
    path(
        'family-group/update/<int:pk>/',
        login_required(FamilyGroupUpdateView.as_view()),
        name='family_group_update'
    ),

    path(
        'family/detail/<int:pk>/',
        login_required(FamilyDetailView.as_view()),
        name='family_detail'
    ),

    path(
        'family-group/detail/<int:pk>/',
        login_required(FamilyGroupDetailView.as_view()),
        name='family_group_detail'
    ),

    path(
        'person/delete/<int:pk>/', login_required(PersonDeleteView.as_view()),
        name='person_delete'
    ),

    path(
        'census/list/', login_required(CensusListView.as_view()),
        name='census_list'
    ),

    path(
        'searches/<slug:id_number>/', login_required(SearchView.as_view()),
        name='search_id_number'
    ),

    path(
        'searches-for-age/<int:age>/',
        login_required(SearchForAgeView.as_view()),
        name='search_age'
    ),

    path(
        'admonitions/list/',
        login_required(AdmonitionListView.as_view()),
        name='admonition_list'
    ),

    path(
        'admonitions/create/',
        login_required(AdmonitionCreateView.as_view()),
        name='admonition_create'
    ),

    path(
        'admonitions/update/<int:pk>/',
        login_required(AdmonitionUpdateView.as_view()),
        name='admonition_update'
    ),

    path(
        'admonitions/delete/<int:pk>/',
        login_required(AdmonitionDeleteView.as_view()),
        name='admonition_delete'
    ),

    path(
        'move-outs/list/',
        login_required(MoveOutListView.as_view()),
        name='move_out_list'
    ),

    path(
        'move-outs/create/',
        login_required(MoveOutCreateView.as_view()),
        name='move_out_create'
    ),

    path(
        'move-outs/update/<int:pk>/',
        login_required(MoveOutUpdateView.as_view()),
        name='move_out_update'
    ),

    path(
        'condominiums/list/',
        login_required(CondominiumListView.as_view()),
        name='condominium_list'
    ),

    path(
        'condominiums/create/',
        login_required(CondominiumCreateView.as_view()),
        name='condominium_create'
    ),

    path(
        'condominiums/detail/<int:pk>/',
        login_required(CondominiumDetailView.as_view()),
        name='condominium_detail'
    ),
]
