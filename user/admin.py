from django.contrib import admin
from .models import Profile, UbchLevel, CommunityLeader, StreetLeader, FamilyGroup, Person
from .forms import UbchLevelAdminForm

class ProfileAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Profile al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Mostrar los campos de la clase
    list_display = ('id_number','user')
admin.site.register(Profile, ProfileAdmin)

class UbchLevelAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo UbchLevel al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    form = UbchLevelAdminForm
    change_form_template = 'user/admin/change_form.html'

    ## Mostrar los campos de la clase
    list_display = ('ubch','profile')
admin.site.register(UbchLevel, UbchLevelAdmin)

class CommunityLeaderAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo CommunityLeader al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Mostrar los campos de la clase
    list_display = ('ubch_level','profile')
admin.site.register(CommunityLeader, CommunityLeaderAdmin)

class StreetLeaderAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo StreetLeader al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Mostrar los campos de la clase
    list_display = ('community_leader','profile')
admin.site.register(StreetLeader, StreetLeaderAdmin)

class FamilyGroupAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo FamilyGroup al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Mostrar los campos de la clase
    list_display = ('street_leader','profile')
admin.site.register(FamilyGroup, FamilyGroupAdmin)

class PersonAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Person al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Mostrar los campos de la clase
    list_display = ('first_name','last_name','id_number')
admin.site.register(Person, PersonAdmin)
