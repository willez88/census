from base.models import CommunalCouncil, Estate, Municipality, Parish, Ubch
from django import forms
from django.contrib.auth.models import User
from django.core import validators

from .models import CommunityLeader, Profile, UbchLevel


class UbchLevelAdminForm(forms.ModelForm):
    """!
    Clase que contiene los campos del formulario

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Estado donde se ecnuetra ubicado el municipio
    estate = forms.ModelChoiceField(
        label='Estado:', queryset=Estate.objects.all(),
        empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'title': 'Seleccione el estado en donde se encuentra ubicada.',
        })
    )

    # Municipio donde se encuentra ubicada la parroquia
    municipality = forms.ModelChoiceField(
        label='Municipio:', queryset=Municipality.objects.all(),
        empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'disabled': 'true',
            'title': 'Seleccione el municipio en donde se encuentra ubicada.',
        })
    )

    # Parroquia donde se encuentra ubicado el consejo comunal
    parish = forms.ModelChoiceField(
        label='Parroquia:', queryset=Parish.objects.all(),
        empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'disabled': 'true',
            'title': 'Seleccione la parroquia en donde se encuentra ubicada.',
        })
    )

    # Ubch donde se encuentra ubicada la parroquia
    ubch = forms.ModelChoiceField(
        label='Ubch:', queryset=Ubch.objects.all(),
        empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'disabled': 'true',
            'title': 'Seleccione la ubch en donde se encuentra ubicada.',
        })
    )


class ProfileForm(forms.ModelForm):
    """!
    Clase que contiene los campos del formulario de perfil del usuario

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
    |GNU Public License versión 2 (GPLv2)</a>
    """

    # Username para identificar al usuario, en este caso se usa la cédula
    username = forms.CharField(
        label='Usuario:', max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-sm', 'data-toggle': 'tooltip',
                'title': 'Indique el nombre de usuario',
            }
        )
    )

    # Nombres del usuario
    first_name = forms.CharField(
        label='Nombres:', max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-sm', 'data-toggle': 'tooltip',
                'title': 'Indique los Nombres',
            }
        )
    )

    # Apellidos del usuario
    last_name = forms.CharField(
        label='Apellidos:', max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-sm', 'data-toggle': 'tooltip',
                'title': 'Indique los Apellidos',
            }
        )
    )

    # Correo del usuario
    email = forms.EmailField(
        label='Correo Electrónico:', max_length=100,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control input-sm', 'data-toggle': 'tooltip',
                'title': 'Indique el correo electrónico'
            }
        )
    )

    phone = forms.CharField(
        label='Teléfono:', max_length=11,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-sm', 'data-toggle': 'tooltip',
                'title': 'Indique el teléfono',
            }
        ),
        validators=[
            validators.RegexValidator(
                r'^[\d]{11}$',
                'Número telefónico inválido'
            ),
        ],
        help_text='Formato: 04160000000'
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise forms.ValidationError('El correo ya está registrado')
        return email

    class Meta:
        """!
        Meta clase del formulario que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'phone'
        ]


class ProfileUpdateForm(ProfileForm):
    """!
    Clase que contiene los campos del formulario para actualizar

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def clean_email(self):
        email = self.cleaned_data['email']
        username = self.cleaned_data.get('username')
        if User.objects.filter(email=email).exclude(username=username):
            raise forms.ValidationError('El correo ya esta registrado')
        return email

    class Meta:
        """!
        Meta clase del formulario que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        model = Profile
        fields = [
            'username', 'first_name', 'last_name', 'email', 'phone'
        ]


class CommunityLeaderForm(ProfileForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        ubch_level = UbchLevel.objects.get(profile=user.profile)
        cl_list = [('', 'Selecione...')]
        for cc in CommunalCouncil.objects.filter(ubch=ubch_level.ubch):
            cl_list.append((cc.id, cc))
        self.fields['communal_council'].choices = cl_list

    communal_council = forms.ChoiceField(
        label='Consejo Comunal:',
        widget=forms.Select(
            attrs={
                'class': 'form-control select2', 'data-toggle': 'tooltip',
                'title': 'Seleccione el consejo comunal',
            }
        )
    )

    def clean_communal_council(self):
        communal_council = self.cleaned_data['communal_council']
        if CommunityLeader.objects.filter(communal_council=communal_council):
            raise forms.ValidationError(
                'Ya existe un usuario asignado a esta comunidad'
            )
        return communal_council

    class Meta:
        """!
        Meta clase del formulario que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'phone',
            'communal_council'
        ]
