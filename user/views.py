import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from base.functions import send_email
from base.models import (
    CommunalCouncil,
    Department,
    Gender,
    Relationship,
    VoteType,
)
from user.functions import generate_password

from .forms import (
    AdmonitionForm,
    CondominiumForm,
    CommunityLeaderForm,
    FamilyGroupForm,
    FamilyGroupUpdateForm,
    MoveOutForm,
    PersonFormSet,
    ProfileUpdateForm,
    StreetLeaderForm,
)
from .models import (
    Admonition,
    Condominium,
    CommunityLeader,
    FamilyGroup,
    FamilyHead,
    MoveOut,
    Payment,
    Person,
    Profile,
    StreetLeader,
    UbchLevel,
)

logger = logging.getLogger('user')


class ProfileUpdateView(UpdateView):
    """!
    Clase que permite a los usuarios actualizar sus datos de perfil

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'user/profile_create.html'
    success_url = reverse_lazy('base:home')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.profile.pk == self.kwargs['pk']:
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get_initial(self):
        """!
        Método que agrega valores predeterminados a los campos del formulario

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Retorna un diccionario con los valores predeterminados
        """

        initial_data = super().get_initial()
        initial_data['username'] = self.object.user.username
        initial_data['first_name'] = self.object.user.first_name
        initial_data['last_name'] = self.object.user.last_name
        initial_data['email'] = self.object.user.email
        return initial_data

    def form_valid(self, form):
        """!
        Metodo que valida si el formulario es correcto

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param form <b>{object}</b> Objeto que contiene el formulario de
            registro
        @return Retorna el formulario validado
        """

        self.object = form.save()
        self.object.id_number = form.cleaned_data['id_number']
        self.object.phone = form.cleaned_data['phone']
        self.object.save()

        user = User.objects.get(username=self.object.user.username)
        user.username = form.cleaned_data['username']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        user.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class CommunityLeaderListView(ListView):
    """!
    Clase que permite a los usuarios del nivel ubch, listar usuarios líderes de
    comunidad

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = CommunityLeader
    template_name = 'user/user_list.html'
    success_url = reverse_lazy('user:community_leader_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.groups.filter(name='Nivel Ubch'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get_queryset(self):
        """!
        Método que obtiene los usuarios líderes de comunidad

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Lista de objetos
        """

        if UbchLevel.objects.filter(profile=self.request.user.profile):
            ubch_level = UbchLevel.objects.get(
                profile=self.request.user.profile
            )
            queryset = CommunityLeader.objects.filter(
                communal_council__ubch=ubch_level.ubch
            )
            return queryset

    def post(self, *args, **kwargs):
        """!
        Función que recibe como parámetro si el usuario está activo o inactivo

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos con el id del curso
        @return Redirige a la vista de listar usuarios líderes de comunidad
        """

        activate = self.request.POST.get('activate')
        deactivate = self.request.POST.get('deactivate')
        status = False

        if activate is not None:
            user_id = activate
            status = True
        elif deactivate is not None:
            user_id = deactivate
            status = False
        else:
            messages.error(
                self.request, 'Esta intentando hacer una acción incorrecta'
            )
        try:
            user = User.objects.get(pk=user_id)
            user.is_active = status
            user.save()
            if status:
                messages.success(
                    self.request, 'Se ha activado el usuario: %s' % (str(user))
                )
            else:
                messages.warning(
                    self.request, 'Se ha inactivado el usuario: %s' %
                    (str(user))
                )
        except Exception as e:
            messages.info(self.request, e)
        return redirect(self.success_url)


class CommunityLeaderFormView(FormView):
    """!
    Clase que permite a los usuarios del nivel ubch, crear usuarios líderes de
    comunidad

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = User
    form_class = CommunityLeaderForm
    template_name = 'user/community_leader_create.html'
    success_url = reverse_lazy('user:community_leader_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.groups.filter(name='Nivel Ubch'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """!
        Metodo que valida si el formulario es correcto

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param form <b>{object}</b> Objeto que contiene el formulario de
            registro
        @return Retorna el formulario validado
        """

        self.object = form.save()
        self.object.username = form.cleaned_data['username']
        self.object.first_name = form.cleaned_data['first_name']
        self.object.last_name = form.cleaned_data['last_name']
        self.object.email = form.cleaned_data['email']
        password = User.objects.make_random_password()
        self.object.set_password(password)
        self.object.is_active = True
        self.object.save()
        self.object.groups.add(Group.objects.get(name='Líder de Comunidad'))

        profile = Profile.objects.create(
            id_number=form.cleaned_data['id_number'],
            phone=form.cleaned_data['phone'],
            user=self.object
        )
        communal_council = CommunalCouncil.objects.get(
            pk=form.cleaned_data['communal_council']
        )
        CommunityLeader.objects.create(
            communal_council=communal_council,
            profile=profile
        )

        admin, admin_email = '', ''
        if settings.ADMINS:
            admin = settings.ADMINS[0][0]
            admin_email = settings.ADMINS[0][1]

        ubch_level = UbchLevel.objects.get(profile=self.request.user.profile)

        sent = send_email(
            self.object.email, 'user/welcome.mail', 'Bienvenido a Censo',
            {
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email, 'ubch': ubch_level.ubch,
                'username': self.object.username, 'password': password,
                'admin': admin, 'admin_email': admin_email,
                'emailapp': settings.EMAIL_HOST_USER,
                'url': get_current_site(self.request).name
            }
        )

        if not sent:
            logger.warning(
                str('Ocurrió un inconveniente al enviar por correo las \
                    credenciales del usuario [%s]' % self.object.username)
            )
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class StreetLeaderListView(ListView):
    """!
    Clase que permite a los usuarios líderes de comunidad listar usuarios
    líderes de calle

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = StreetLeader
    template_name = 'user/user_list.html'
    success_url = reverse_lazy('user:street_leader_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.groups.filter(name='Líder de Comunidad'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get_queryset(self):
        """!
        Método que obtiene los usuarios líderes de calle

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Lista de objetos
        """

        if CommunityLeader.objects.filter(profile=self.request.user.profile):
            community_leader = CommunityLeader.objects.get(
                profile=self.request.user.profile
            )
            queryset = StreetLeader.objects.filter(
                community_leader=community_leader
            )
            return queryset

    def post(self, *args, **kwargs):
        """!
        Función que recibe como parámetro si el usuario está activo o inactivo

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos con el id del curso
        @return Redirige a la vista de listar usuarios líderes de calle
        """

        activate = self.request.POST.get('activate')
        deactivate = self.request.POST.get('deactivate')
        status = False

        if activate is not None:
            user_id = activate
            status = True
        elif deactivate is not None:
            user_id = deactivate
            status = False
        else:
            messages.error(
                self.request, 'Esta intentando hacer una acción incorrecta'
            )
        try:
            user = User.objects.get(pk=user_id)
            user.is_active = status
            user.save()
            if status:
                messages.success(
                    self.request, 'Se ha activado el usuario: %s' % (str(user))
                )
            else:
                messages.warning(
                    self.request, 'Se ha inactivado el usuario: %s' %
                    (str(user))
                )
        except Exception as e:
            messages.info(self.request, e)
        return redirect(self.success_url)


class StreetLeaderFormView(FormView):
    """!
    Clase que permite a los usuarios del líder de comunidad, crear usuarios
    líderes de calle

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = User
    form_class = StreetLeaderForm
    template_name = 'user/street_leader_create.html'
    success_url = reverse_lazy('user:street_leader_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.groups.filter(name='Líder de Comunidad'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """!
        Metodo que valida si el formulario es correcto

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param form <b>{object}</b> Objeto que contiene el formulario de
            registro
        @return Retorna el formulario validado
        """

        self.object = form.save()
        self.object.username = form.cleaned_data['username']
        self.object.first_name = form.cleaned_data['first_name']
        self.object.last_name = form.cleaned_data['last_name']
        self.object.email = form.cleaned_data['email']
        password = User.objects.make_random_password()
        self.object.set_password(password)
        self.object.is_active = True
        self.object.save()
        self.object.groups.add(Group.objects.get(name='Líder de Calle'))

        profile = Profile.objects.create(
            id_number=form.cleaned_data['id_number'],
            phone=form.cleaned_data['phone'],
            user=self.object
        )
        community_leader = CommunityLeader.objects.get(
            profile=self.request.user.profile
        )
        StreetLeader.objects.create(
            community_leader=community_leader,
            profile=profile,
            bridge=form.cleaned_data['bridge']
        )

        admin, admin_email = '', ''
        if settings.ADMINS:
            admin = settings.ADMINS[0][0]
            admin_email = settings.ADMINS[0][1]

        sent = send_email(
            self.object.email, 'user/welcome.mail', 'Bienvenido a Censo',
            {
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email,
                'ubch': community_leader.communal_council.ubch,
                'username': self.object.username, 'password': password,
                'admin': admin, 'admin_email': admin_email,
                'emailapp': settings.EMAIL_HOST_USER,
                'url': get_current_site(self.request).name
            }
        )

        if not sent:
            logger.warning(
                str('Ocurrió un inconveniente al enviar por correo las \
                    credenciales del usuario [%s]' % self.object.username)
            )
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class FamilyGroupListView(ListView):
    """!
    Clase que permite a los usuarios líderes de calle, listar usuarios grupo
    familiar

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = FamilyGroup
    template_name = 'user/family_group_list.html'
    success_url = reverse_lazy('user:family_group_list')
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.groups.filter(name='Líder de Calle'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get_queryset(self):
        """!
        Método que obtiene los usuarios grupo familiar

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Lista de objetos
        """

        if StreetLeader.objects.filter(profile=self.request.user.profile):
            street_leader = StreetLeader.objects.get(
                profile=self.request.user.profile
            )
            return FamilyGroup.objects.filter(
                street_leader=street_leader
            ).select_related('profile__user').prefetch_related('person_set')
        return FamilyGroup.objects.none()

    def post(self, *args, **kwargs):
        """!
        Función que recibe como parámetro si el usuario está activo o inactivo

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos con el id del curso
        @return Redirige a la vista de listar usuarios grupos familiares
        """

        activate = self.request.POST.get('activate')
        deactivate = self.request.POST.get('deactivate')
        status = False

        if activate is not None:
            user_id = activate
            status = True
        elif deactivate is not None:
            user_id = deactivate
            status = False
        else:
            messages.error(
                self.request, 'Esta intentando hacer una acción incorrecta'
            )
        try:
            user = User.objects.get(pk=user_id)
            user.is_active = status
            user.save()
            if status:
                messages.success(
                    self.request, 'Se ha activado el usuario: %s' % (str(user))
                )
            else:
                messages.warning(
                    self.request, 'Se ha inactivado el usuario: %s' %
                    (str(user))
                )
        except Exception as e:
            messages.info(self.request, e)
        return redirect(self.success_url)


class FamilyGroupCreateTemplateView(TemplateView):
    """!
    Clase que permite a los usuarios del líder de calle, crear usuarios grupos
    familiares

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    template_name = 'user/family_group_create.html'

    def dispatch(self, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.groups.filter(name='Líder de Calle'):
            return super().dispatch(*args, **kwargs)
        return redirect('base:error_403')


class FamilyGroupSaveView(View):
    """!
    Clase que permite a los usuarios del líder de calle crear usuarios grupos
    familiares

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def dispatch(self, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.groups.filter(name='Líder de Calle'):
            return super().dispatch(*args, **kwargs)
        return redirect('base:error_403')

    def post(self, request, *args, **kwargs):
        record = json.loads(request.body.decode('utf-8'))
        family_group_form = FamilyGroupForm(record)
        if not family_group_form.is_valid():
            return JsonResponse(
                {
                    'status': False, 'message': 'Error en los campos',
                    'errors': {
                        'family_group': family_group_form.errors,
                        'people': [{}]
                    }
                },
                status=422
            )
        i = 0
        data = {}
        for person in record['people']:
            for key, value in person.items():
                form_name = 'form-' + str(i) + '-' + key
                data[form_name] = value
            i = i + 1
        data['form-TOTAL_FORMS'] = i
        data['form-INITIAL_FORMS'] = 0
        personformset = PersonFormSet(data)
        if not personformset.is_valid():
            return JsonResponse(
                {
                    'status': False,
                    'message': 'Error en los campos',
                    'errors': {
                        'people': personformset.errors,
                        'general_error': personformset.non_form_errors()
                    }
                },
                status=422
            )
        password = generate_password()
        user = User.objects.create_user(
            record['username'],
            record['email'],
            password,
        )
        # user.first_name = record['first_name']
        # user.last_name = record['last_name']
        user.is_active = False
        user.save()
        user.groups.add(Group.objects.get(name='Grupo Familiar'))
        profile = Profile.objects.create(
            # phone=record['phone'],
            user=user
        )
        street_leader = StreetLeader.objects.get(
            profile=self.request.user.profile
        )
        department = Department.objects.get(pk=record['department_id'])
        family_group = FamilyGroup.objects.create(
            street_leader=street_leader,
            profile=profile,
            department=department,
        )
        c = 1
        for person in record['people']:
            gender = Gender.objects.get(pk=person['gender_id'])
            vote_type = VoteType.objects.get(pk=person['vote_type_id'])
            relationship = Relationship.objects.get(
                pk=person['relationship_id']
            )
            if person['has_id_number'] == 'y':
                if person['family_head']:
                    value = True
                else:
                    value = False
                Person.objects.create(
                    first_name=person['first_name'],
                    last_name=person['last_name'],
                    id_number=person['id_number'],
                    email=person['email'],
                    phone=person['phone'],
                    birthdate=person['birthdate'],
                    admission_date=person['admission_date'],
                    gender=gender,
                    vote_type=vote_type,
                    relationship=relationship,
                    family_head=value,
                    family_group=family_group
                )
            else:
                p = Person.objects.get(
                    family_group=family_group, family_head=True
                )
                Person.objects.create(
                    first_name=person['first_name'],
                    last_name=person['last_name'],
                    id_number=p.id_number + '-' + str(c),
                    email=person['email'],
                    phone=person['phone'],
                    birthdate=person['birthdate'],
                    admission_date=person['admission_date'],
                    gender=gender,
                    vote_type=vote_type,
                    relationship=relationship,
                    family_head=False,
                    family_group=family_group
                )
                c = c + 1
        admin, admin_email = '', ''
        if settings.ADMINS:
            admin = settings.ADMINS[0][0]
            admin_email = settings.ADMINS[0][1]

        send_email(
            user.email, 'user/welcome.mail', 'Bienvenido a Censo',
            {
                'first_name': self.request.user.first_name,
                'last_name': self.request.user.last_name,
                'email': self.request.user.email,
                'ubch': street_leader.community_leader.communal_council.ubch,
                'username': user.username, 'password': password,
                'admin': admin, 'admin_email': admin_email,
                'emailapp': settings.EMAIL_HOST_USER,
                'url': get_current_site(self.request).name
            }
        )
        return JsonResponse(
            {
                'status': True,
                'message': 'Datos guardados con éxito',
                'redirect': '/user/family-group/list/',
            },
            status=200
        )

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class FamilyGroupEditTemplateView(TemplateView):
    """!
    Clase que permite a los usuarios del líder de calle, actualizar usuarios
    grupos familiares

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    template_name = 'user/family_group_create.html'

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        street_leader = StreetLeader.objects.get(
            profile=self.request.user.profile
        )
        if self.request.user.groups.filter(name='Líder de Calle')\
                and FamilyGroup.objects.filter(
                    id=kwargs['pk'], street_leader=street_leader):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        family_group_id = kwargs['pk']
        if FamilyGroup.objects.filter(id=family_group_id):
            context['family_group'] = FamilyGroup.objects.get(
                id=family_group_id
            )
        return context


class FamilyGroupUpdateView(View):
    """!
    Clase que permite a los usuarios del líder de calle, actualizar usuarios
    grupos familiares

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        street_leader = StreetLeader.objects.get(
            profile=self.request.user.profile
        )
        if self.request.user.groups.filter(name='Líder de Calle') \
                and FamilyGroup.objects.filter(
                    id=kwargs['pk'], street_leader=street_leader):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def put(self, *args, **kwargs):
        family_group_id = kwargs['pk']
        family_group = FamilyGroup.objects.get(pk=family_group_id)
        record = json.loads(self.request.body.decode('utf-8'))
        family_group_form = FamilyGroupUpdateForm(record)

        i = 0
        data = {}
        for person in record['people']:
            for key, value in person.items():
                form_name = 'form-' + str(i) + '-' + key
                data[form_name] = value
            i = i + 1
        data['form-TOTAL_FORMS'] = i
        data['form-INITIAL_FORMS'] = 0
        personformset = PersonFormSet(data)
        if not personformset.is_valid():
            return JsonResponse(
                {
                    'status': False,
                    'message': 'Error en los campos',
                    'errors': {
                        'people': personformset.errors,
                        'general_error': personformset.non_form_errors()
                    }
                },
                status=422
            )
        if not family_group_form.is_valid():
            return JsonResponse(
                {
                    'status': False, 'message': 'Error en los campos',
                    'errors': {
                        'family_group': family_group_form.errors,
                        'people': personformset.errors,
                    }
                },
                status=422
            )
        department = Department.objects.get(pk=record['department_id'])
        family_group.department = department
        family_group.save()
        c = Person.objects.filter(
            family_group=family_group, id_number__contains='-'
        ).count() + 1
        for person in record['people']:
            gender = Gender.objects.get(pk=person['gender_id'])
            vote_type = VoteType.objects.get(pk=person['vote_type_id'])
            relationship = Relationship.objects.get(
                pk=person['relationship_id']
            )
            if person['has_id_number'] == 'y':
                Person.objects.update_or_create(
                    id_number=person['id_number'],
                    defaults={
                        'first_name': person['first_name'],
                        'last_name': person['last_name'],
                        'id_number': person['id_number'],
                        'email': person['email'],
                        'phone': person['phone'],
                        'birthdate': person['birthdate'],
                        'admission_date': person['admission_date'],
                        'gender': gender,
                        'vote_type': vote_type,
                        'relationship': relationship,
                        'family_head': person['family_head'],
                        'family_group': family_group
                    }
                )
            elif person['has_id_number'] == 'n':
                p = Person.objects.get(
                    family_group=family_group, family_head=True
                )
                Person.objects.update_or_create(
                    id_number=person['id_number'],
                    defaults={
                        'first_name': person['first_name'],
                        'last_name': person['last_name'],
                        'id_number': p.id_number + '-' + str(c),
                        'email': person['email'],
                        'phone': person['phone'],
                        'birthdate': person['birthdate'],
                        'admission_date': person['admission_date'],
                        'gender': gender,
                        'vote_type': vote_type,
                        'relationship': relationship,
                        'family_head': person['family_head'],
                        'family_group': family_group
                    }
                )
                c = c + 1
        return JsonResponse(
            {
                'status': True,
                'message': 'Datos actualizados con éxito',
                'redirect': '/user/family-group/list/',
            },
            status=200
        )


class FamilyDetailView(DetailView):
    """!
    Clase que permite a los usuarios del líder de comunidad ver detalles de
    grupos familiares

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = FamilyGroup
    template_name = 'user/family_detail.html'

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        group1 = self.request.user.groups.filter(name='Líder de Comunidad')
        group2 = self.request.user.groups.filter(name='Grupo Familiar')
        family_group_id = kwargs['pk']
        family_group = FamilyGroup.objects.filter(
            id=family_group_id, profile__user=self.request.user
        )
        if group1 or (group2 and family_group):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')


class FamilyGroupDetailView(View):
    """!
    Clase que permite a los usuarios del líder de calle, ver detalles de
    usuarios grupos familiares

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        street_leader = StreetLeader.objects.get(
            profile=self.request.user.profile
        )
        if self.request.user.groups.filter(name='Líder de Calle') \
                and FamilyGroup.objects.filter(
                    id=kwargs['pk'], street_leader=street_leader
                ):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get(self, request, *args, **kwargs):
        family_group_id = kwargs['pk']
        family_group = FamilyGroup.objects.get(pk=family_group_id)
        people = Person.objects.filter(family_group=family_group)
        person = []
        for p in people:
            person.append({
                'id': p.id, 'first_name': p.first_name,
                'last_name': p.last_name, 'has_id_number': 'y',
                'id_number': p.id_number, 'email': p.email,
                'vote_type_id': p.vote_type.id if p.vote_type else '',
                'relationship_id': p.relationship.id if p.relationship else '',
                'phone': p.phone, 'birthdate': p.birthdate,
                'admission_date': p.admission_date,
                'gender_id': p.gender.id if p.gender else '',
                'family_head': p.family_head,
            })
        record = {
            'id': family_group.id,
            'username': family_group.profile.user.username,
            'email': family_group.profile.user.email,
            'building_id': family_group.department.building.id,
            'department_id': family_group.department.id,
            'people': person
        }
        return JsonResponse({'status': True, 'record': record}, status=200)


class PersonDeleteView(View):
    """!
    Clase que permite a los usuarios del líder de calle, eliminar integrantes
    del grupo familiar (En desarrollo)

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        street_leader = StreetLeader.objects.get(
            profile=self.request.user.profile
        )
        person_id = kwargs['pk']
        person = Person.objects.filter(
            id=person_id, family_group__street_leader=street_leader
        )
        group = self.request.user.groups.filter(name='Líder de Calle')
        if group and person:
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get(self, request, *args, **kwargs):
        person_id = kwargs['pk']
        Person.objects.filter(pk=person_id).delete()
        return JsonResponse(
            {'status': 'true', 'message': 'Datos eliminados con éxito'},
            status=200
        )


class CensusListView(ListView):
    """!
    Clase que permite a los usuarios líderes de comunidad ver todos los
    datos de la residencia

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = StreetLeader
    template_name = 'user/census_list.html'

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.groups.filter(name='Líder de Comunidad'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get_queryset(self):
        """!
        Método que obtiene los usuarios líderes de calle

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Lista de objetos
        """

        if CommunityLeader.objects.filter(profile=self.request.user.profile):
            community_leader = CommunityLeader.objects.get(
                profile=self.request.user.profile
            )
            return StreetLeader.objects.filter(
                community_leader__communal_council=community_leader.communal_council
            ).prefetch_related(
                'familygroup_set__person_set'  # Optimiza las consultas
            )
        return StreetLeader.objects.none()


class SearchView(View):
    """!
    Clase que retorna un json con los datos

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        group1 = self.request.user.groups.filter(name='Líder de Comunidad')
        group2 = self.request.user.groups.filter(name='Líder de Calle')
        if group1 or group2:
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get(self, request, *args, **kwargs):
        id_number = kwargs['id_number']
        if CommunityLeader.objects.filter(profile__user=self.request.user):
            community_leader = CommunityLeader.objects.get(profile__user=self.request.user)
            communal_council = community_leader.communal_council
            person = Person.objects.filter(
                id_number=id_number,
                family_group__street_leader__community_leader__communal_council=communal_council
            )
        elif StreetLeader.objects.filter(profile__user=self.request.user):
            street_leader = StreetLeader.objects.get(profile__user=self.request.user)
            person = Person.objects.filter(id_number=id_number, family_group__street_leader=street_leader)
        # person = Person.objects.filter(id_number=id_number)
        if not person:
            return JsonResponse(
                {'record': {}, 'error': 'Persona no encontrada.'}, status=200
            )
        person = Person.objects.get(id_number=id_number)
        family_group = person.family_group
        people = family_group.person_set.all()
        person_list = []
        for person in people:
            relationship = person.relationship
            person_list.append({
                'first_name': person.first_name,
                'last_name': person.last_name, 'has_id_number': 'y',
                'id_number': person.id_number, 'email': person.email,
                'vote_type': person.vote_type.name if person.vote_type else '',
                'relationship': relationship.name if relationship else '',
                'phone': person.phone, 'birthdate': person.birthdate,
                'admission_date': person.admission_date,
                'gender': person.gender.name if person.gender else '',
                'age': person.age(),
                'family_head': person.family_head
            })
        record = {
            'username': family_group.profile.user.username,
            'email': family_group.profile.user.email,
            'department': str(family_group.department),
            'people': person_list
        }
        return JsonResponse(
            {'record': record}, status=200
        )


class SearchForAgeView(View):
    """!
    Clase que retorna un json con datos filtrados por edad

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        group1 = self.request.user.groups.filter(name='Líder de Comunidad')
        group2 = self.request.user.groups.filter(name='Líder de Calle')
        if group1 or group2:
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get(self, request, *args, **kwargs):
        age = kwargs['age']
        if CommunityLeader.objects.filter(profile__user=self.request.user):
            community_leader = CommunityLeader.objects.get(profile__user=self.request.user)
            communal_council = community_leader.communal_council
            people = Person.objects.filter(
                family_group__street_leader__community_leader__communal_council=communal_council
            )
        elif StreetLeader.objects.filter(profile__user=self.request.user):
            street_leader = StreetLeader.objects.get(profile__user=self.request.user)
            people = Person.objects.filter(
                family_group__street_leader=street_leader
            )
        # people = Person.objects.all()
        person_list = []
        counter = 0
        for person in people:
            if person.age() == age:
                person_list.append({
                    'first_name': person.first_name,
                    'last_name': person.last_name,
                    'id_number': person.id_number,
                    'birthdate': person.birthdate,
                    'admission_date': person.admission_date,
                    'gender': person.gender.name if person.gender else '',
                    'age': person.age(),
                    'department': str(person.family_group.department),
                })
                counter = counter + 1
        record = {
            'total_children': counter,
            'people': person_list
        }
        return JsonResponse(
            {'record': record}, status=200
        )


class AdmonitionListView(ListView):
    """!
    Clase que lista las amonestaciones

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = Admonition
    template_name = 'user/admonition_list.html'

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.groups.filter(name='Líder de Comunidad'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')


class AdmonitionCreateView(CreateView):
    """!
    Clase que permite a un usuario registrar amonestaciones

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = Admonition
    form_class = AdmonitionForm
    template_name = 'user/admonition_create.html'
    success_url = reverse_lazy('user:admonition_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.groups.filter(name='Líder de Comunidad'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get_form_kwargs(self):
        """!
        Método que permite pasar el usuario actualmente logueado al formulario

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Retorna un diccionario con el usuario actualmente logueado
        """

        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """!
        Función que valida si el formulario está correcto

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param form <b>{object}</b> Objeto que contiene el formulario
        @return super <b>{object}</b> Formulario validado
        """

        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class AdmonitionUpdateView(UpdateView):
    """!
    Clase que permite a un usuario actualizar amonestaciones

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = Admonition
    form_class = AdmonitionForm
    template_name = 'user/admonition_create.html'
    success_url = reverse_lazy('user:admonition_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        admonition_id = self.kwargs['pk']
        group = self.request.user.groups.filter(name='Líder de Comunidad')
        if Admonition.objects.filter(
            pk=admonition_id, user=self.request.user
        ).exists() and group:
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get_form_kwargs(self):
        """!
        Método que permite pasar el usuario actualmente logueado al formulario

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Retorna un diccionario con el usuario actualmente logueado
        """

        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class AdmonitionDeleteView(DeleteView):
    """!
    Clase que permite a un usuario eliminar los datos de una amonestación

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = Admonition
    template_name = 'user/admonition_delete.html'
    success_url = reverse_lazy('user:admonition_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        admonition_id = self.kwargs['pk']
        group = self.request.user.groups.filter(name='Líder de Comunidad')
        if Admonition.objects.filter(
            pk=admonition_id, user=self.request.user
        ).exists() and group:
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def delete(self, request, *args, **kwargs):
        """!
        Función que retorna el mensaje de confirmación de la eliminación

        @author William Páez (wpaez at cenditel.gob.ve)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene los datos de la
            petición
        @param *args <b>{tuple}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return super <b>{object}</b> Objeto con el mensaje de confirmación
            de la eliminación
        """

        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


class MoveOutListView(ListView):
    """!
    Clase que lista las mudanzas

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = MoveOut
    template_name = 'user/move_out_list.html'

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.groups.filter(name='Líder de Calle'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')
    
    def get_queryset(self):
        """!
        Función que obtiene la lista de solicitudes de mudanzas asociadas al usuario

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return queryset <b>{object}</b> lista de mudanzas asociadas al usuario
        """

        queryset = MoveOut.objects.filter(user=self.request.user)
        return queryset


class MoveOutCreateView(CreateView):
    """!
    Clase que permite a un usuario registrar solicitudes de mudanzas

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = MoveOut
    form_class = MoveOutForm
    template_name = 'user/move_out_create.html'
    success_url = reverse_lazy('user:move_out_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        if self.request.user.groups.filter(name='Líder de Calle'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get_form_kwargs(self):
        """!
        Método que permite pasar el usuario actualmente logueado al formulario

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Retorna un diccionario con el usuario actualmente logueado
        """

        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """!
        Función que valida si el formulario está correcto

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param form <b>{object}</b> Objeto que contiene el formulario
        @return super <b>{object}</b> Formulario validado
        """

        self.object = form.save(commit=False)
        street_leader = StreetLeader.objects.get(bridge=form.cleaned_data['bridge'])
        self.object.street_leader = str(street_leader.profile.user)
        person = form.cleaned_data['person']
        self.object.person = str(person)
        self.object.from_address = str(person.family_group.department)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class MoveOutUpdateView(UpdateView):
    """!
    Clase que permite a un usuario actualizar las mudanzas

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = MoveOut
    form_class = MoveOutForm
    template_name = 'user/move_out_create.html'
    success_url = reverse_lazy('user:move_out_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        move_out_id = self.kwargs['pk']
        group = self.request.user.groups.filter(name='Líder de Calle')
        if not MoveOut.objects.filter(
            pk=move_out_id, user=self.request.user
        ).exists():
            return redirect('base:error_403')
        move_out = MoveOut.objects.get(pk=move_out_id)
        if move_out and not move_out.approved and group:
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get_form_kwargs(self):
        """!
        Método que permite pasar el usuario actualmente logueado al formulario

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Retorna un diccionario con el usuario actualmente logueado
        """

        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_initial(self):
        """!
        Función que agrega valores predeterminados a los campos del formulario

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return initial_data <b>{object}</b> Valores predeterminado de los
            campos del formulario
        """

        initial_data = super().get_initial()
        id_number = self.object.person.split('-')
        person = Person.objects.get(id_number=id_number[1].strip())
        initial_data['person'] = person
        initial_data['block'] = self.object.department.building.bridge.block
        initial_data['bridge'] = self.object.department.building.bridge
        initial_data['building'] = self.object.department.building
        return initial_data
    
    def form_valid(self, form):
        """!
        Función que valida si el formulario está correcto

        @author William Páez (paez.william8 at gmail.com)
        @date 06-07-2018
        @param self <b>{object}</b> Objeto que instancia la clase
        @param form <b>{object}</b> Objeto que contiene el formulario
        @return super <b>{object}</b> Formulario validado
        """

        self.object = form.save(commit=False)
        street_leader = StreetLeader.objects.get(bridge=form.cleaned_data['bridge'])
        self.object.street_leader = str(street_leader.profile.user)
        person = form.cleaned_data['person']
        self.object.person = str(person)
        self.object.from_address = str(person.family_group.department)
        self.object.save()
        return super().form_valid(form)


class CondominiumListView(ListView):
    """!
    Clase que lista los cobros del condominio

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = Condominium
    template_name = 'user/condominium_list.html'
    success_url = reverse_lazy('user:condominium_list')
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        group1 = self.request.user.groups.filter(name='Líder de Comunidad')
        group2 = self.request.user.groups.filter(name='Líder de Calle')
        group3 = self.request.user.groups.filter(name='Grupo Familiar')
        if group1 or group2 or group3:
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')
    
    def get_queryset(self):
        """!
        Función que obtiene la lista de pagos de condominio asociadas al usuario

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return queryset <b>{object}</b> lista de mudanzas asociadas al usuario
        """

        if StreetLeader.objects.filter(profile=self.request.user.profile):
            street_leader = StreetLeader.objects.get(
                profile=self.request.user.profile
            )
            queryset = Condominium.objects.filter(user=street_leader.community_leader.profile.user)
            return queryset
        elif FamilyGroup.objects.filter(profile__user=self.request.user):
            family_group = FamilyGroup.objects.get(
                profile__user=self.request.user
            )
            queryset = Condominium.objects.filter(
                user=family_group.street_leader.community_leader.profile.user
            )
            return queryset

        queryset = Condominium.objects.filter(user=self.request.user)
        return queryset
    
    def post(self, *args, **kwargs):
        """!
        Función que recibe como parámetro pagado o no pagado

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos con el id
        @return Redirige a la vista detalles de pagos
        """

        activate = self.request.POST.get('activate')
        deactivate = self.request.POST.get('deactivate')
        status = False

        if activate is not None:
            condominium_id = activate
            status = True
        elif deactivate is not None:
            condominium_id = deactivate
            status = False
        else:
            messages.error(
                self.request, 'Esta intentando hacer una acción incorrecta'
            )
        try:
            condominium = Condominium.objects.get(pk=condominium_id)
            condominium.closing = status
            condominium.save()
            if status:
                messages.success(
                    self.request, 'Cerrado: %s' % (str(condominium))
                )
            else:
                messages.warning(
                    self.request, 'Abierto: %s' % (str(condominium))
                )
        except Exception as e:
            messages.info(self.request, e)
        return redirect(self.success_url)


class CondominiumCreateView(CreateView):
    """!
    Clase que permite a un usuario registrar pagos de condominium

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = Condominium
    form_class = CondominiumForm
    template_name = 'user/condominium_create.html'
    success_url = reverse_lazy('user:condominium_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        # usuario comunidad
        user_id = self.request.user.id
        if self.request.user.groups.filter(name='Líder de Comunidad') and user_id == 3:
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def form_valid(self, form):
        """!
        Función que valida si el formulario está correcto

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param form <b>{object}</b> Objeto que contiene el formulario
        @return super <b>{object}</b> Formulario validado
        """

        family_heads = []
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.user = self.request.user
            self.object.save()
            for department in Department.objects.all():
                family_groups = department.familygroup_set.filter(
                    street_leader__community_leader__profile__user=self.request.user
                )
                if family_groups:
                    payment = Payment.objects.create(
                        department=department,
                        condominium=self.object,
                        user=family_groups[0].street_leader.profile.user
                    )
                    total_family_group = family_groups.count()
                    for family_group in family_groups:
                        if family_group.person_set.filter(family_head=True).exists():
                            people = family_group.person_set.filter(family_head=True)
                            if people.count() > 1:
                                family_heads.append(people.first())
                                FamilyHead.objects.create(
                                    payer='{} {}'.format(people.first().first_name, people.first().last_name),
                                    id_number=people.first().id_number,
                                    amount=(self.object.rate * self.object.amount) / total_family_group,
                                    payment=payment
                                )
                            else:
                                FamilyHead.objects.create(
                                    payer='{} {}'.format(people.first().first_name, people.first().last_name),
                                    id_number=people.first().id_number,
                                    amount=(self.object.rate * self.object.amount) / total_family_group,
                                    payment=payment
                                )
        if family_heads:
            messages.warning(
                self.request, 'Jefe Familiar repetido: %s' % (family_heads)
            )
        return super().form_valid(form)


class CondominiumDetailView(DetailView):
    """!
    Clase que permite a un usuario registrar pagos de condominium

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = Condominium
    template_name = 'user/condominium_detail.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no
            es su perfil
        """

        group1 = self.request.user.groups.filter(name='Líder de Comunidad')
        group2 = self.request.user.groups.filter(name='Líder de Calle')
        group3 = self.request.user.groups.filter(name='Grupo Familiar')
        if group1 or group2 or group3:
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def post(self, *args, **kwargs):
        """!
        Función que recibe como parámetro pagado o no pagado

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos con el id
        @return Redirige a la vista detalles de pagos
        """

        activate_paid = self.request.POST.get('activate_paid')
        deactivate_paid = self.request.POST.get('deactivate_paid')
        activate_exonerated = self.request.POST.get('activate_exonerated')
        deactivate_exonerated = self.request.POST.get('deactivate_exonerated')

        if activate_paid is not None:
            family_head = FamilyHead.objects.get(pk=activate_paid)
            family_head.paid = True
            family_head.save()
            messages.success(
                self.request, 'Pagado: %s' % (str(family_head))
            )
        elif deactivate_paid is not None:
            family_head = FamilyHead.objects.get(pk=deactivate_paid)
            family_head.paid = False
            family_head.save()
            messages.warning(
                self.request, 'No Pagado: %s' % (str(family_head))
            )
        elif activate_exonerated is not None:
            family_head = FamilyHead.objects.get(pk=activate_exonerated)
            family_head.exonerated = True
            family_head.paid = False
            family_head.save()
            messages.success(
                self.request, 'Exonerado: %s' % (str(family_head))
            )
        elif deactivate_exonerated is not None:
            family_head = FamilyHead.objects.get(pk=deactivate_exonerated)
            family_head.exonerated = False
            family_head.save()
            messages.warning(
                self.request, 'No Exonerado: %s' % (str(family_head))
            )
        else:
            messages.error(
                self.request, 'Esta intentando hacer una acción incorrecta'
            )
        return redirect(self.get_success_url())

    def get_success_url(self):
        condomonium = get_object_or_404(Condominium, pk=self.kwargs['pk'])
        return reverse_lazy(
            'user:condominium_detail',
            kwargs={
                'pk': condomonium.id,
            }
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        street_leaders = StreetLeader()
        user = self.request.user
        if StreetLeader.objects.filter(community_leader__profile__user=user):
            street_leaders = StreetLeader.objects.filter(
                community_leader__profile__user=user
            )
        elif StreetLeader.objects.filter(profile__user=user):
            street_leaders = StreetLeader.objects.filter(
                profile__user=user
            )
        elif FamilyGroup.objects.filter(profile__user=user):
            family_group = FamilyGroup.objects.get(profile__user=user)
            street_leaders = StreetLeader.objects.filter(
                profile=family_group.street_leader.profile
            )
            context['person'] = family_group.person_set.get(family_head=True)
        amount_street_leaders = {}
        total_sum = 0
        for street_leader in street_leaders:
            payments = self.object.payment_set.filter(user=street_leader.profile.user)
            total_exonerated = 0
            total_paid = 0
            total_unpaid = 0
            sum = 0
            total_departments = 0
            for payment in payments:
                for family_head in payment.familyhead_set.all():
                    if family_head.paid and not family_head.exonerated:
                        sum = sum + family_head.amount
                        total_sum = total_sum + family_head.amount
                        total_paid = total_paid + 1
                    elif family_head.exonerated:
                        total_exonerated = total_exonerated + 1
                    elif not family_head.paid:
                        total_unpaid = total_unpaid + 1
                total_departments = total_departments + 1
            amount_street_leaders[
                str(street_leader.profile.user)
            ] = (
                sum,
                sum/self.object.rate,
                total_paid,
                total_unpaid,
                total_paid + total_unpaid,
                total_exonerated,
                total_departments,
            )
        context['amount_street_leaders'] = amount_street_leaders
        context['total_sum'] = (total_sum, total_sum/self.object.rate)

        # Paginación de los pagos
        payment_list = self.object.payment_set.all()
        paginator = Paginator(payment_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        return context
