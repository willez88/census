from django.contrib import admin

from .forms import CommunalCouncilAdminForm, UbchAdminForm
from .models import CommunalCouncil, Relationship, Ubch, VoteType


class UbchAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Ubch al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    form = UbchAdminForm
    change_form_template = 'base/admin/change_form.html'

    # Mostrar los campos
    list_display = ('name',)


class CommunalCouncilAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo CommunalCouncil al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    form = CommunalCouncilAdminForm
    change_form_template = 'base/admin/change_form2.html'

    # Mostrar los campos
    list_display = ('rif', 'name', 'ubch',)


class VoteTypeAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo VoteType al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('name',)


class RelationshipAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Relationship al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('name',)


admin.site.register(Ubch, UbchAdmin)
admin.site.register(CommunalCouncil, CommunalCouncilAdmin)
admin.site.register(VoteType, VoteTypeAdmin)
admin.site.register(Relationship, RelationshipAdmin)
