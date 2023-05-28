from django import forms
from django.contrib.auth.models import User
from django.core import validators
from django.forms import BaseFormSet, formset_factory

from base.models import (
    Block,
    Bridge,
    Building,
    CommunalCouncil,
    Department,
    Estate,
    Gender,
    Municipality,
    Parish,
    Relationship,
    Ubch,
    VoteType,
)

from .models import (
    Admonition,
    CommunityLeader,
    Person,
    Profile,
    StreetLeader,
    UbchLevel,
)


class UbchLevelAdminForm(forms.ModelForm):
    """!
    Clase que contiene los campos del formulario

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
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
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
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

    # Cédula de identidad
    id_number = forms.CharField(
        label='Cédula de Identidad:', max_length=8,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-sm', 'data-toggle': 'tooltip',
                'title': 'Indique la cédula de identidad',
            }
        ),
        validators=[
            validators.RegexValidator(
                r'^([\d]{7}|[\d]{8})$',
                'Este campo es inválido'
            ),
        ],
        help_text='Formato: 0000000 ó 00000000',
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

    def clean_id_number(self):
        id_number = self.cleaned_data['id_number']
        if Profile.objects.filter(id_number=id_number):
            raise forms.ValidationError('La cédula ya está registrada')
        return id_number

    class Meta:
        """!
        Meta clase del formulario que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'id_number',
            'phone'
        ]


class ProfileUpdateForm(ProfileForm):
    """!
    Clase que contiene los campos del formulario para actualizar

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def clean_username(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(
            username=username
        ).exclude(pk=self.instance.user.id)
        if self.instance and self.instance.pk and not user:
            return username
        raise forms.ValidationError('Nombre de usuario ya está registrado')

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).exclude(
            username=self.instance.user.username
        )
        if user:
            raise forms.ValidationError('El correo ya esta registrado')
        return email

    def clean_id_number(self):
        id_number = self.cleaned_data['id_number']
        return id_number

    class Meta:
        """!
        Meta clase del formulario que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        model = Profile
        fields = [
            'username', 'first_name', 'last_name', 'email', 'id_number',
            'phone',
        ]


class CommunityLeaderForm(ProfileForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        ubch_level = UbchLevel.objects.get(profile=user.profile)
        communalcouncil_list = [('', 'Selecione...')]
        ubch = ubch_level.ubch
        for communal_council in CommunalCouncil.objects.filter(ubch=ubch):
            communalcouncil_list.append(
                (communal_council.id, communal_council)
            )
        self.fields['communal_council'].choices = communalcouncil_list

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
            'username', 'first_name', 'last_name', 'email', 'id_number',
            'phone',
        ]


class StreetLeaderForm(ProfileForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        community_leader = CommunityLeader.objects.get(profile=user.profile)
        block_list = [('', 'Selecione...')]
        communal_council = community_leader.communal_council
        for block in Block.objects.filter(communal_council=communal_council):
            block_list.append((block.id, block))
        self.fields['block'].choices = block_list

    block = forms.ChoiceField(
        label='Bloque:',
        widget=forms.Select(
            attrs={
                'class': 'form-control select2', 'data-toggle': 'tooltip',
                'title': 'Seleccione el bloque',
                'onchange': "combo_update(this.value, 'base', 'Bridge',\
                    'block', 'pk', 'name', 'id_bridge')",
            }
        )
    )

    bridge = forms.ModelChoiceField(
        label='Puente:', queryset=Bridge.objects.all(),
        empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'disabled': 'true',
            'title': 'Seleccione el puente.',
        })
    )

    def clean_bridge(self):
        bridge = self.cleaned_data['bridge']
        if StreetLeader.objects.filter(bridge=bridge):
            raise forms.ValidationError(
                'Ya existe un usuario asignado a este puente'
            )
        return bridge

    class Meta:
        """!
        Meta clase del formulario que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'id_number',
            'phone',
        ]


class FamilyGroupForm(forms.Form):
    """!
    Clase que contiene los campos del formulario

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Nombre de usuario
    username = forms.CharField(
        label='Usuario:', max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-sm', 'data-toggle': 'tooltip',
                'title': 'Indique el nombre de usuario',
            }
        )
    )

    # Correo electrónico
    email = forms.EmailField(
        label='Correo Electrónico:', max_length=100,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control input-sm', 'data-toggle': 'tooltip',
                'title': 'Indique el correo electrónico'
            }
        )
    )

    # Edificio
    building_id = forms.ModelChoiceField(
        label='Edificio:', queryset=Building.objects.all(),
        empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'title': 'Seleccione el edificio',
        })
    )

    # Departamento
    department_id = forms.ModelChoiceField(
        label='Departamento:', queryset=Department.objects.all(),
        empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'title': 'Seleccione el departamento',
        })
    )

    def clean_username(self):
        """!
        Método que valida si el usuario ya existe

        @author William Páez (paez.william8 at gmail.com)
        """

        username = self.cleaned_data['username']
        if User.objects.filter(username=username):
            raise forms.ValidationError(
                'Este campo ya está registrado'
            )
        return username

    def clean_email(self):
        """!
        Método que valida si el email ya existe

        @author William Páez (paez.william8 at gmail.com)
        """

        email = self.cleaned_data['email']
        if User.objects.filter(email=email):
            raise forms.ValidationError('Este campo ya está registrado')
        return email


class PersonForm(forms.Form):
    """!
    Clase que contiene los campos del formulario

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

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

    # ¿Tiene cédula de identidad?
    has_id_number = forms.ChoiceField(
        label='¿Tiene cédula de identidad?',
        choices=[
            ('y', 'Si'),
            ('n', 'No'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'title': 'Seleccione una opción',
        })
    )

    # Cédula de identidad
    id_number = forms.CharField(
        label='Cédula de identidad:', max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-sm', 'data-toggle': 'tooltip',
                'title': 'Indique la cédula de identidad',
            }
        ),
        validators=[
            validators.RegexValidator(
                r'^(([\d]{7}|[\d]{8})|([\d]{7}|[\d]{8})-([\d]{1}|[\d]{2}))$',
                'Este campo es inválido'
            ),
        ],
        required=False
    )

    # Correo electrónico
    email = forms.EmailField(
        label='Correo Electrónico:', max_length=100,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control input-sm', 'data-toggle': 'tooltip',
                'title': 'Indique el correo electrónico'
            }
        ),
        required=False,
    )

    # Número telefónico
    phone = forms.CharField(
        label='Teléfono:', max_length=11,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-sm', 'data-toggle': 'tooltip',
                'title': 'Indique el número telefónico',
            }
        ),
        validators=[
            validators.RegexValidator(
                r'^[\d]{11}$',
                'Este campo es inválido. Formato: 04160000000'
            ),
        ],
        help_text='Formato: 04160000000',
        required=False,
    )

    # Fecha de nacimiento
    birthdate = forms.DateField(
        label='Fecha de Nacimiento:',
        widget=forms.DateInput(
            attrs={
                'class': 'form-control form-control-lg datepicker',
                'data-toggle': 'tooltip',
                'title': 'Indique la fecha de nacimiento.',
            }
        )
    )

    # Género
    gender_id = forms.ModelChoiceField(
        label='Género:', queryset=Gender.objects.all(),
        empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'title': 'Seleccione el género',
        })
    )

    # Tipo de voto
    vote_type_id = forms.ModelChoiceField(
        label='Tipo de Voto:', queryset=VoteType.objects.all(),
        empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'title': 'Seleccione el tipo de voto',
        })
    )

    # Parentesco
    relationship_id = forms.ModelChoiceField(
        label='Parentesco:', queryset=Relationship.objects.all(),
        empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'title': 'Seleccione el parentesco',
        })
    )

    # Jefe familiar
    family_head = forms.BooleanField(
        label='Jefe Familiar:', required=False
    )

    def clean_id_number(self):
        """!
        Método que valida si la cédula ya existe y es correcta

        @author William Páez (paez.william8 at gmail.com)
        """

        id_number = self.cleaned_data['id_number']
        has_id_number = self.cleaned_data.get('has_id_number')
        if has_id_number == 'y' and not id_number:
            raise forms.ValidationError('Este campo es obligatorio.')
        return id_number


class BasePersonFormSet(BaseFormSet):
    def clean(self):
        """Checks that no two articles have the same title."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on
            # its own
            return
        i = 0
        for form in self.forms:
            if form.cleaned_data['family_head']:
                i = i + 1
        if i >= 2 or i == 0:
            raise forms.ValidationError(
                'Solo puede haber 1 jefe familiar'
            )


PersonFormSet = formset_factory(
    PersonForm, min_num=1, validate_min=True, formset=BasePersonFormSet
)


class AdmonitionForm(forms.ModelForm):
    """!
    Clase que contiene los campos del formulario

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Persona
    person = forms.ModelChoiceField(
        label='Residente:',
        queryset=Person.objects.all(),
        empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'title': 'Seleccione el residente.',
        })
    )

    # Fecha
    date = forms.DateField(
        label='Fecha:',
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control form-control-lg',
                'data-toggle': 'tooltip',
                'title': 'Indique la fecha.',
            }
        )
    )

    # Descripción
    description = forms.CharField(
        label='Descripción:',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control input-sm', 'data-toggle': 'tooltip',
                'title': 'Indique la descrición',
            }
        ), required=False
    )

    class Meta:
        """!
        Meta clase del formulario que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        model = Admonition
        fields = ['date', 'description', 'person',]
