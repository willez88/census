from django.contrib import admin

from .forms import UbchLevelAdminForm
from .models import (
    Admonition,
    Condominium,
    CommunityLeader,
    FamilyGroup,
    FamilyHead,
    MoveOut,
    Payment,
    Person,
    Profile,
    StreetLeader,
    UbchLevel,
)


class ProfileAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Profile al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('phone', 'user')


class UbchLevelAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo UbchLevel al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
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
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('communal_council', 'profile')


class StreetLeaderAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo StreetLeader al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos
    list_display = ('community_leader', 'profile')


class FamilyGroupAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo FamilyGroup al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos de la clase
    list_display = ('street_leader', 'profile')

    # Aplica select2 en campos desplegables
    autocomplete_fields = (
        'department',
    )


class PersonAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Person al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos de la clase
    list_display = (
        'first_name', 'last_name', 'id_number', 'email', 'phone',
        'family_head', 'vote_type', 'relationship', 'family_group',
    )

    # Buscar por campos
    search_fields = (
        'first_name', 'last_name', 'id_number',
    )


class MoveOutAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo MoveOut al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos de la clase
    list_display = (
        'person', 'from_address', 'department', 'street_leader', 'date',
        'description', 'approved',
    )

    # Buscar por campos
    search_fields = (
        'person', 'from_address', 'street_leader',
    )


class AdmonitionAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Admonition al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos de la clase
    list_display = (
        'person', 'date', 'description', 'user',
    )

    # Buscar por campos
    search_fields = (
        'person__first_name', 'person_last_name', 'person_id_number',
    )


class CondominiumAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Condominium al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos de la clase
    list_display = (
        'date', 'rate', 'amount', 'user',
    )

    # Buscar por campos
    search_fields = (
        'date',
    )


class PaymentAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo Payment al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos de la clase
    list_display = (
        'department', 'condominium', 'user',
    )

    # Buscar por campos
    search_fields = (
        'department__name',
    )

    # Filtrar por campos
    list_filter = ('condominium__date',)


class FamilyHeadAdmin(admin.ModelAdmin):
    """!
    Clase que agrega modelo FamilyHead al panel administrativo

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Mostrar los campos de la clase
    list_display = (
        'payer', 'id_number', 'paid', 'exonerated', 'amount', 'payment',
    )

    # Buscar por campos
    search_fields = (
        'payer', 'id_number',
    )

    # Filtrar por campos
    list_filter = ('payment__condominium__date',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(UbchLevel, UbchLevelAdmin)
admin.site.register(CommunityLeader, CommunityLeaderAdmin)
admin.site.register(StreetLeader, StreetLeaderAdmin)
admin.site.register(FamilyGroup, FamilyGroupAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(MoveOut, MoveOutAdmin)
admin.site.register(Admonition, AdmonitionAdmin)
admin.site.register(Condominium, CondominiumAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(FamilyHead, FamilyHeadAdmin)
