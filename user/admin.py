from django.contrib import admin
from .models import Profile, UbchLevel, StreetLeader

class ProfileAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Profile al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Mostrar los campos de la clase
    list_display = ('user',)
admin.site.register(Profile, ProfileAdmin)

class UbchLevelAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo UbchLevel al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Mostrar los campos de la clase
    list_display = ('ubch','profile')
admin.site.register(UbchLevel, UbchLevelAdmin)

class StreetLeaderAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo StreetLeader al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Mostrar los campos de la clase
    list_display = ('ubch_level','profile')
admin.site.register(StreetLeader, StreetLeaderAdmin)
