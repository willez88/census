from django.contrib import admin
from .models import Ubch, CommunalCouncil
from .forms import UbchAdminForm, CommunalCouncilAdminForm

class UbchAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Ubch al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    form = UbchAdminForm
    change_form_template = 'base/admin/change_form.html'

    ## Mostrar los campos de la clase
    list_display = ('name',)
admin.site.register(Ubch, UbchAdmin)

class CommunalCouncilAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo CommunalCouncil al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    form = CommunalCouncilAdminForm
    change_form_template = 'base/admin/change_form2.html'

    ## Mostrar los campos de la clase
    list_display = ('rif','name','ubch',)
admin.site.register(CommunalCouncil, CommunalCouncilAdmin)
