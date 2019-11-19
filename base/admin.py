from django.contrib import admin
from .models import Ubch
from .forms import UbchAdminForm

class UbchAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Ubch al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    form = UbchAdminForm
    change_form_template = 'user/admin/change_form.html'

    ## Mostrar los campos de la clase
    list_display = ('name',)
admin.site.register(Ubch, UbchAdmin)
