from django.db import models


class Country(models.Model):
    """!
    Clase que contiene los paises

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Nombre del pais
    name = models.CharField('nombre', max_length=80)

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre del país
        """

        return self.name

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'País'
        verbose_name_plural = 'Países'


class Estate(models.Model):
    """!
    Clase que contiene los estados

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Nombre del Estado
    name = models.CharField('nombre', max_length=50)

    # Pais en donde esta ubicado el Estado
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, verbose_name='país'
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre del estado
        """

        return self.name

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'


class Municipality(models.Model):
    """!
    Clase que contiene los municipios

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Nombre del Municipio
    name = models.CharField('nombre', max_length=50)

    # Estado en donde se encuentra el Municipio
    estate = models.ForeignKey(
        Estate, on_delete=models.CASCADE, verbose_name='estado'
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre del municipio
        """

        return self.name

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'


class Parish(models.Model):
    """!
    Clase que contiene las parroquias

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Nombre de la Parroquia
    name = models.CharField('nombre', max_length=50)

    # Municipio en el que se encuentra ubicada la Parroquia
    municipality = models.ForeignKey(
        Municipality, on_delete=models.CASCADE, verbose_name='municipio'
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre de la parroquia
        """

        return self.name

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Parroquia'
        verbose_name_plural = 'Parroquias'


class Ubch(models.Model):
    """!
    Clase que contiene los datos de una UBCH

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Código de la ubch
    code = models.CharField('código', max_length=15)

    # Nombre de la UBCH
    name = models.CharField('nombre', max_length=500)

    # Parroquia donde se encuentra ubicada la ubch
    parish = models.ForeignKey(
        Parish, on_delete=models.CASCADE, verbose_name='parroquia'
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre
        """

        return self.name

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Ubch'
        verbose_name_plural = 'Ubchs'


class CommunalCouncil(models.Model):
    """!
    Clase que contiene los datos de un consejo comunal

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Número de rif del Consejo Comunal
    rif = models.CharField(
        max_length=10, unique=True
    )

    # Nombre del Consejo Comunal
    name = models.CharField('nombre', max_length=500)

    # Relación con el modelo Ubch
    ubch = models.ForeignKey(
        Ubch, on_delete=models.CASCADE, verbose_name='ubch'
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el rif y el nombre
        """

        return self.rif + ' | ' + self.name

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Consejo comunal'
        verbose_name_plural = 'Consejos comunales'


class VoteType(models.Model):
    """!
    Clase que contiene los tipo de votos

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Nombre del tipo de voto
    name = models.CharField('nombre', max_length=80)

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre del tipo de voto
        """

        return self.name

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Tipo de voto'
        verbose_name_plural = 'Tipos de voto'


class Relationship(models.Model):
    """!
    Clase que contiene los parentescos

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='​http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Nombre del parentesco
    name = models.CharField(max_length=20)

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre del parentesco
        """

        return self.name

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Parentesco'
        verbose_name_plural = 'Parentescos'
