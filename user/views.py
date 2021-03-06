import json
import logging
import re

from base.functions import send_email
from base.models import CommunalCouncil, Relationship, VoteType
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    FormView, ListView, TemplateView, UpdateView, View,
)

from .forms import CommunityLeaderForm, ProfileForm, ProfileUpdateForm
from .models import (
    CommunityLeader, FamilyGroup, Person, Profile, StreetLeader, UbchLevel,
)

logger = logging.getLogger('user')


class ProfileUpdateView(UpdateView):
    """!
    Clase que permite a los usuarios actualizar sus datos de perfil

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
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
        else:
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
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
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
        else:
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
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
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
        else:
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
    Clase que permite a los usuarios líderes de comunidad, listar usuarios
    líderes de calle

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
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
        else:
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
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    model = User
    form_class = ProfileForm
    template_name = 'user/profile_create.html'
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
        else:
            return redirect('base:error_403')

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
            phone=form.cleaned_data['phone'],
            user=self.object
        )

        community_leader = CommunityLeader.objects.get(
            profile=self.request.user.profile
        )
        StreetLeader.objects.create(
            community_leader=community_leader,
            profile=profile
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
        print(form.errors)
        return super().form_invalid(form)


class FamilyGroupListView(ListView):
    """!
    Clase que permite a los usuarios líderes de calle, listar usuarios grupo
    familiar

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
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
        else:
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
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
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

        if self.request.user.groups.filter(name='Líder de Calle'):
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('base:error_403')


class FamilyGroupSaveView(View):
    """!
    Clase que permite a los usuarios del líder de calle, crear usuarios grupos
    familiares

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
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

        if self.request.user.groups.filter(name='Líder de Calle'):
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('base:error_403')

    def post(self, request, *args, **kwargs):
        record = json.loads(request.body.decode('utf-8'))
        errors = {}
        required_field = 'Este campo es obligatorio'

        # Validar nombre de usuario
        if not record['username']:
            errors['username'] = ['nombre de usuario: este campo es requerido']
        elif User.objects.filter(username=record['username']):
            errors['username'] = ['nombre de usuario: el usuario ya existe']

        # Vaidar correo del usuario
        result = re.match(
            r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', record['email']
        )
        if not result:
            errors['email'] = ['correo electrónico: el campo es inválido']

        # Validar nombres
        # if not record['first_name']:
        #   errors['first_name'] = ['nombres: este campo es requerido']

        # Validar apellidos
        # if not record['last_name']:
        #   errors['last_name'] = ['apellidos: este campo es requerido']

        # if Profile.objects.filter(id_number=record['id_number']):
        #   errors['id_number'] = ['cédula de identidad: el campo ya existe']

        i = 0
        j = 0
        for person in record['people']:
            field_0 = 'first_name_' + str(i)
            field_1 = 'last_name_' + str(i)
            field_2 = 'id_number_' + str(i)
            field_3 = 'email_' + str(i)
            field_4 = 'phone_' + str(i)
            field_5 = 'vote_type_id_' + str(i)
            field_6 = 'relationship_id_' + str(i)

            if person['family_head']:
                j = j + 1

            # Validar nombres
            if not person['first_name']:
                errors[field_0] = [
                    'nombres_' + str(i) + ': este campo es requerido'
                ]

            # Validar apellidos
            if not person['last_name']:
                errors[field_1] = [
                    'apellidos_' + str(i) + ': este campo es requerido'
                ]

            # Vaidar cédula de identidad
            if person['has_id_number'] == 'y':
                result = re.match(
                    r'^(([\d]{7}|[\d]{8})|([\d]{7}|[\d]{8}-([\d]{1}|[\d]{2})))$',
                    person['id_number']
                )
                if not result:
                    errors[field_2] = [
                        'cédula de identidad_' + str(i) +
                        ': el campo es inválido'
                    ]
                elif Person.objects.filter(id_number=person['id_number']):
                    errors[field_2] = [
                        'cédula de identidad_' + str(i) +
                        ': el campo ya existe'
                    ]

            # Vaidar correo de la persona
            if not person['email'] == '':
                result = re.match(
                    r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$',
                    person['email']
                )
                if not result:
                    errors[field_3] = [
                        'correo electrónico_' + str(i) +
                        ': el campo es inválido'
                    ]

            # Validar teléfono
            if not person['phone'] == '':
                result = re.match(r'^[\d]{11}$', person['phone'])
                if not result:
                    errors[field_4] = [
                        'teléfono_' + str(i) + ': el campo es inválido'
                    ]

            # Validar tipo de voto
            if not person['vote_type_id']:
                errors[field_5] = [
                    'tipo de voto_' + str(i) + ': este campo es requerido'
                ]

            # Validar tipo de voto
            if not person['relationship_id']:
                errors[field_6] = [
                    'parentesco_' + str(i) + ': este campo es requerido'
                ]

            i = i + 1

        if j >= 2 or j == 0:
            errors['family_head'] = [
                'jefe familiar: solo puede haber 1 jefe familiar'
            ]

        if errors:
            return JsonResponse(
                {
                    'status': 'false', 'message': 'Error en los campos',
                    'errors': errors
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
        family_group = FamilyGroup.objects.create(
            street_leader=street_leader,
            profile=profile
        )

        c = 1
        for person in record['people']:
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
            {'status': 'true', 'message': 'Datos guardados con éxito'},
            status=200
        )


class FamilyGroupEditTemplateView(TemplateView):
    """!
    Clase que permite a los usuarios del líder de calle, actualizar usuarios
    grupos familiares

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
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
        else:
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
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
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
        else:
            return redirect('base:error_403')

    def put(self, request, *args, **kwargs):
        errors = {}
        family_group_id = kwargs['pk']
        family_group = FamilyGroup.objects.get(pk=family_group_id)
        record = json.loads(request.body.decode('utf-8'))

        i = 0
        j = 0
        for person in record['people']:
            field_0 = 'first_name_' + str(i)
            field_1 = 'last_name_' + str(i)
            field_2 = 'id_number_' + str(i)
            field_3 = 'email_' + str(i)
            field_4 = 'phone_' + str(i)
            field_5 = 'vote_type_id_' + str(i)
            field_6 = 'relationship_id_' + str(i)

            if person['family_head']:
                j = j + 1

            # Validar nombres
            if not person['first_name']:
                errors[field_0] = [
                    'nombres_' + str(i) + ': este campo es requerido'
                ]

            # Validar apellidos
            if not person['last_name']:
                errors[field_1] = [
                    'apellidos_' + str(i) + ': este campo es requerido'
                ]

            # Vaidar cédula de identidad
            if person['has_id_number'] == 'y':
                result = re.match(
                    r'^(([\d]{7}|[\d]{8})|([\d]{7}|[\d]{8}-([\d]{1}|[\d]{2})))$',
                    person['id_number']
                )
                if not result:
                    errors[field_2] = [
                        'cédula de identidad_' + str(i) +
                        ': el campo es inválido'
                    ]

            # Vaidar correo de la persona
            if not person['email'] == '':
                result = re.match(
                    r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$',
                    person['email']
                )
                if not result:
                    errors[field_3] = [
                        'correo electrónico_' + str(i) +
                        ': el campo es inválido'
                    ]

            # Validar teléfono
            if not person['phone'] == '':
                result = re.match(r'^[\d]{11}$', person['phone'])
                if not result:
                    errors[field_4] = [
                        'teléfono_' + str(i) + ': el campo es inválido'
                    ]

            # Validar tipo de voto
            if not person['vote_type_id']:
                errors[field_5] = [
                    'tipo de voto_' + str(i) + ': este campo es requerido'
                ]

            # Validar parentesco
            if not person['relationship_id']:
                errors[field_6] = [
                    'parentesco_' + str(i) + ': este campo es requerido'
                ]

            i = i + 1

        if j >= 2 or j == 0:
            errors['family_head'] = [
                'jefe familiar: solo puede haber 1 jefe familiar'
            ]

        if errors:
            return JsonResponse(
                {
                    'status': 'false', 'message': 'Error en los campos',
                    'errors': errors
                },
                status=422
            )

        c = Person.objects.filter(
            family_group=family_group, id_number__contains='-'
        ).count() + 1

        for person in record['people']:
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
                        'vote_type': vote_type,
                        'relationship_id': relationship,
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
                        'vote_type': vote_type,
                        'relationship': relationship,
                        'family_head': person['family_head'],
                        'family_group': family_group
                    }
                )
                c = c + 1

        return JsonResponse(
            {'status': 'true', 'message': 'Datos actualizados con éxito'},
            status=200
        )


class FamilyGroupDetailView(View):
    """!
    Clase que permite a los usuarios del líder de calle, ver detalles de
    usuarios grupos familiares

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
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
        else:
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
                'phone': p.phone, 'family_head': p.family_head
            })
        record = {
            'id': family_group.id,
            'username': family_group.profile.user.username,
            'email': family_group.profile.user.email, 'people': person
        }
        return JsonResponse({'status': 'true', 'record': record}, status=200)


class PersonDeleteView(View):
    """!
    Clase que permite a los usuarios del líder de calle, eliminar integrantes
    del grupo familiar (En desarrollo)

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
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
        family_group = FamilyGroup.objects.get(street_leader=street_leader)
        if self.request.user.groups.filter(name='Líder de Calle') \
                and Person.objects.filter(
                    id=kwargs['pk'], family_group=family_group
                ):
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('base:error_403')

    def get(self, request, *args, **kwargs):
        person_id = kwargs['pk']
        Person.objects.filter(pk=person_id).delete()
        return JsonResponse(
            {'status': 'true', 'message': 'Datos eliminados con éxito'},
            status=200
        )
