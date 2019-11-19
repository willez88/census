from django.db import models
from django.contrib.auth.models import User
from base.models import Ubch

class Profile(models.Model):
    """!
    Clase que contiene los datos del perfil de usuario

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Cédula de identidad
    id_number = models.CharField('cédula de identidad', max_length=8, unique=True)

    ## Relación con el modelo User
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='usuario')

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre y apellido
        """

        return self.user.first_name + ' ' + self.user.last_name + ' - ' + self.id_number

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

class UbchLevel(models.Model):
    """!
    Clase que contiene los datos de un usuario nivel de ubch

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Relación con el modelo Ubch
    ubch = models.OneToOneField(Ubch, on_delete=models.CASCADE, verbose_name='ubch')

    ## Relación con el modelo Profile
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, verbose_name='perfil', null=True)

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre y apellido
        """

        return str(self.profile) + ' | ' + str(self.ubch) + \
            ' - ' + str(self.ubch.parish) + ' - ' + str(self.ubch.parish.municipality) + \
            ' - ' + str(self.ubch.parish.municipality.estate)

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Nivel ubch'
        verbose_name_plural = 'Niveles ubch'

class CommunityLeader(models.Model):
    """!
    Clase que contiene los datos de un usuario líder de comunidad

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Relación con el modelo UbchLevel
    ubch_level = models.ForeignKey(UbchLevel, on_delete=models.CASCADE, verbose_name='nivel ubch')

    ## Relación con el modelo Profile
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, verbose_name='perfil', null=True)

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre y apellido
        """

        return str(self.ubch_level)


    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Líder de comunidad'
        verbose_name_plural = 'Líderes de comunidad'

class StreetLeader(models.Model):
    """!
    Clase que contiene los datos de un usuario líder de calle

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>GNU Public License versión 2 (GPLv2)</a>
    """

    ## Relación con el modelo CommunityLeader
    community_leader = models.ForeignKey(CommunityLeader, on_delete=models.CASCADE, verbose_name='líder de comunidad')

    ## Relación con el modelo Profile
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, verbose_name='perfil', null=True)

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre y apellido
        """

        return str(self.community_leader)

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Líder de calle'
        verbose_name_plural = 'Líderes de calle'
