from django.contrib import admin

from .forms import (
    CommunalCouncilAdminForm,
    UbchAdminForm
)
from .models import (
    Block,
    Bridge,
    Building,
    CommunalCouncil,
    Department,
    Gender,
    Relationship,
    Ubch,
    VoteType
)


class UbchAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Ubch al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    form = UbchAdminForm
    change_form_template = 'base/admin/change_form.html'

    # Mostrar los campos
    list_display = ('name', 'parish',)


class CommunalCouncilAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo CommunalCouncil al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    form = CommunalCouncilAdminForm
    change_form_template = 'base/admin/change_form2.html'

    # Mostrar los campos
    list_display = ('rif', 'name', 'ubch',)


class BlockAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Block al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('name', 'communal_council',)


class BridgeAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Bridge al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('name', 'block',)


class BuildingAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Building al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('name', 'bridge',)


class DepartmentAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Department al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('name', 'building',)


class VoteTypeAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo VoteType al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('name',)


class RelationshipAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Relationship al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('name',)


class GenderAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Gender al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('name',)


admin.site.register(Ubch, UbchAdmin)
admin.site.register(CommunalCouncil, CommunalCouncilAdmin)
admin.site.register(Block, BlockAdmin)
admin.site.register(Bridge, BridgeAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(VoteType, VoteTypeAdmin)
admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(Gender, GenderAdmin)
