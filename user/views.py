from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import Profile, UbchLevel, CommunityLeader, StreetLeader
from .forms import ProfileForm, ProfileUpdateForm
from django.views.generic import ListView, FormView, UpdateView
from django.contrib import messages
from django.contrib.auth.models import User, Group
from base.functions import send_email
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

class ProfileUpdateView(UpdateView):
    """!
    Clase que permite a los usuarios actualizar sus datos de perfil

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'user/profile_create.html'
    success_url = reverse_lazy('base:home')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no es su perfil
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
        @param form <b>{object}</b> Objeto que contiene el formulario de registro
        @return Retorna el formulario validado
        """

        self.object = form.save()
        self.object.id_number = form.cleaned_data['id_number']
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
    Clase que permite a los usuarios del nivel ubch, listar usuarios líderes de comunidad

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    model = CommunityLeader
    template_name = 'user/user_list.html'
    success_url = reverse_lazy('user:community_leader_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no es su perfil
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
            ubch_level = UbchLevel.objects.get(profile=self.request.user.profile)
            queryset = CommunityLeader.objects.filter(ubch_level=ubch_level)
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
            messages.error(self.request, 'Esta intentando hacer una acción incorrecta')
        try:
            user = User.objects.get(pk=user_id)
            user.is_active = status
            user.save()
            if status:
                messages.success(self.request, 'Se ha activado el usuario: %s' % (str(user)))
            else:
                messages.warning(self.request, 'Se ha inactivado el usuario: %s' % (str(user)))
        except Exception as e:
            messages.info(self.request, e)
        return redirect(self.success_url)

class CommunityLeaderFormView(FormView):
    """!
    Clase que permite a los usuarios del nivel ubch, crear usuarios líderes de comunidad

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    model = User
    form_class = ProfileForm
    template_name = 'user/profile_create.html'
    success_url = reverse_lazy('user:community_leader_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no es su perfil
        """

        if self.request.user.groups.filter(name='Nivel Ubch'):
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect('base:error_403')

    def form_valid(self, form):
        """!
        Metodo que valida si el formulario es correcto

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param form <b>{object}</b> Objeto que contiene el formulario de registro
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
            user= self.object
        )

        ubch_level = UbchLevel.objects.get(profile=self.request.user.profile)
        community_leader = CommunityLeader.objects.create(
            ubch_level = ubch_level,
            profile = profile
        )

        admin, admin_email = '', ''
        if settings.ADMINS:
            admin = settings.ADMINS[0][0]
            admin_email = settings.ADMINS[0][1]

        send_email(self.object.email, 'user/welcome.mail', 'Bienvenido a Censo', {'first_name':self.request.user.first_name,
            'last_name':self.request.user.last_name, 'email':self.request.user.email,'ubch':ubch_level.ubch,
            'username':self.object.username, 'password':password, 'admin':admin, 'admin_email':admin_email,
            'emailapp':settings.EMAIL_HOST_USER, 'url':get_current_site(self.request).name
        })
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

class StreetLeaderListView(ListView):
    """!
    Clase que permite a los usuarios líderes de comunidad, listar usuarios líderes de calle

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    model = StreetLeader
    template_name = 'user/user_list.html'
    success_url = reverse_lazy('user:street_leader_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no es su perfil
        """

        if self.request.user.groups.filter(name='Líder de Comunidad'):
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

        if CommunityLeader.objects.filter(profile=self.request.user.profile):
            community_leader = CommunityLeader.objects.get(profile=self.request.user.profile)
            queryset = StreetLeader.objects.filter(community_leader=community_leader)
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
            messages.error(self.request, 'Esta intentando hacer una acción incorrecta')
        try:
            user = User.objects.get(pk=user_id)
            user.is_active = status
            user.save()
            if status:
                messages.success(self.request, 'Se ha activado el usuario: %s' % (str(user)))
            else:
                messages.warning(self.request, 'Se ha inactivado el usuario: %s' % (str(user)))
        except Exception as e:
            messages.info(self.request, e)
        return redirect(self.success_url)

class StreetLeaderFormView(FormView):
    """!
    Clase que permite a los usuarios del líder de comunidad, crear usuarios líderes de calle

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    model = User
    form_class = ProfileForm
    template_name = 'user/profile_create.html'
    success_url = reverse_lazy('user:street_leader_list')

    def dispatch(self, request, *args, **kwargs):
        """!
        Metodo que valida si el usuario del sistema tiene permisos para entrar a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Redirecciona al usuario a la página de error de permisos si no es su perfil
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
        @param form <b>{object}</b> Objeto que contiene el formulario de registro
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
            user= self.object
        )

        community_leader = CommunityLeader.objects.get(profile=self.request.user.profile)
        street_leader = StreetLeader.objects.create(
            community_leader = community_leader,
            profile = profile
        )

        admin, admin_email = '', ''
        if settings.ADMINS:
            admin = settings.ADMINS[0][0]
            admin_email = settings.ADMINS[0][1]

        send_email(self.object.email, 'user/welcome.mail', 'Bienvenido a Censo', {'first_name':self.request.user.first_name,
            'last_name':self.request.user.last_name, 'email':self.request.user.email,'ubch':community_leader.ubch_level.ubch,
            'username':self.object.username, 'password':password, 'admin':admin, 'admin_email':admin_email,
            'emailapp':settings.EMAIL_HOST_USER, 'url':get_current_site(self.request).name
        })
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)
