from django import forms
from base.models import Estate, Municipality, Parish

class UbchAdminForm(forms.ModelForm):
    """!
    Clase que contiene los campos del formulario

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Estado donde se ecnuetra ubicado el municipio
    estate = forms.ModelChoiceField(
        label='Estado:', queryset=Estate.objects.all(), empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip',
            'title': 'Seleccione el estado en donde se encuentra ubicada.',
        })
    )

    ## Municipio donde se encuentra ubicada la parroquia
    municipality = forms.ModelChoiceField(
        label='Municipio:', queryset=Municipality.objects.all(), empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip', 'disabled': 'true',
            'title': 'Seleccione el municipio en donde se encuentra ubicada.',
        })
    )

    ## Parroquia donde se encuentra ubicado el consejo comunal
    parish = forms.ModelChoiceField(
        label='Parroquia:', queryset=Parish.objects.all(), empty_label='Seleccione...',
        widget=forms.Select(attrs={
            'class': 'form-control select2', 'data-toggle': 'tooltip', 'disabled': 'true',
            'title': 'Seleccione la parroquia en donde se encuentra ubicada.',
        })
    )
