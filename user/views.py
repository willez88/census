import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.sites.shortcuts import get_current_site
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

from .forms import (
    AdmonitionForm,
    CommunityLeaderForm,
    FamilyGroupForm,
    MoveOutForm,
    PersonFormSet,
    ProfileUpdateForm,
    StreetLeaderForm,
)
from .models import (
    Admonition,
    CommunityLeader,
    FamilyGroup,
    MoveOut,
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
        print(form.errors)
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
        print(form.errors)
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
            queryset = FamilyGroup.objects.filter(street_leader=street_leader)
            return queryset

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
        password = User.objects.make_random_password()
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

        if self.request.user.groups.filter(name='Líder de Comunidad'):
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
                'gender_id': p.gender.id if p.gender else '',
                'family_head': p.family_head
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
            queryset = StreetLeader.objects.filter(
                community_leader=community_leader
            )
            return queryset


class SearchTemplateView(TemplateView):
    """!
    Clase que permite a los usuarios líder de comunidad hacer búsquedas

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    template_name = 'user/search.html'


class SearchView(View):
    """!
    Clase que retorna un json con los datos

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def get(self, request, *args, **kwargs):
        id_number = kwargs['id_number']
        if CommunityLeader.objects.filter(profile__user=self.request.user):
            community_leader = CommunityLeader.objects.get(profile__user=self.request.user)
            person = Person.objects.filter(id_number=id_number, family_group__street_leader__community_leader=community_leader)
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

    def get(self, request, *args, **kwargs):
        age = kwargs['age']
        if CommunityLeader.objects.filter(profile__user=self.request.user):
            community_leader = CommunityLeader.objects.get(profile__user=self.request.user)
            people = Person.objects.filter(
                family_group__street_leader__community_leader=community_leader
            ).order_by(
                'family_group__department__building__bridge__block__name',
                'family_group__department__building__name',
                'family_group__department__name'
            )
        elif StreetLeader.objects.filter(profile__user=self.request.user):
            street_leader = StreetLeader.objects.get(profile__user=self.request.user)
            people = Person.objects.filter(
                family_group__street_leader=street_leader
            ).order_by(
                'family_group__department__building__bridge__block__name',
                'family_group__department__building__name',
                'family_group__department__name'
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

        if self.request.user.groups.filter(name='Líder de Comunidad'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')


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

        if self.request.user.groups.filter(name='Líder de Comunidad'):
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

        group = self.request.user.groups.filter(name='Líder de Calle')
        move_out = MoveOut()
        if MoveOut.objects.filter(
            pk=self.kwargs['pk'], user=self.request.user
        ):
            move_out = MoveOut.objects.get(pk=self.kwargs['pk'])
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
