from django.contrib import admin

from .forms import UbchLevelAdminForm
from .models import (
    CommunityLeader, FamilyGroup, Person, Profile, StreetLeader, UbchLevel
)


class ProfileAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Profile al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('phone', 'user')


class UbchLevelAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo UbchLevel al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    form = UbchLevelAdminForm
    change_form_template = 'user/admin/change_form.html'

    # Mostrar los campos
    list_display = ('ubch', 'profile')


class CommunityLeaderAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo CommunityLeader al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('communal_council', 'profile')


class StreetLeaderAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo StreetLeader al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('community_leader', 'profile')


class FamilyGroupAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo FamilyGroup al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos de la clase
    list_display = ('street_leader', 'profile')


class PersonAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Person al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos de la clase
    list_display = ('first_name', 'last_name', 'id_number')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(UbchLevel, UbchLevelAdmin)
admin.site.register(CommunityLeader, CommunityLeaderAdmin)
admin.site.register(StreetLeader, StreetLeaderAdmin)
admin.site.register(FamilyGroup, FamilyGroupAdmin)
admin.site.register(Person, PersonAdmin)
