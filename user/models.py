import datetime

from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.core import validators
from django.db import models

from base.models import (
    Bridge,
    CommunalCouncil,
    Department,
    Gender,
    Relationship,
    Ubch,
    VoteType,
)


class Profile(models.Model):
    """!
    Clase que contiene los datos del perfil de usuario

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Cédula de identidad
    id_number = models.CharField(
        'cédula de identidad',
        max_length=8,
        unique=True,
        null=True,
        validators=[
            validators.RegexValidator(
                r'^([\d]{7}|[\d]{8})$',
                'Introduzca una cédula de identidad válida'
            ),
        ],
    )

    # Teléfono (04160000000)
    phone = models.CharField('teléfono', max_length=11, null=True, blank=True)

    # Relación con el modelo User
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name='usuario'
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre y apellido
        """

        return self.user.first_name + ' ' + self.user.last_name

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
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Relación con el modelo Ubch
    ubch = models.OneToOneField(
        Ubch, on_delete=models.CASCADE, verbose_name='ubch'
    )

    # Relación con el modelo Profile
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, verbose_name='perfil', null=True
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre y apellido
        """

        return str(self.profile) + ' | ' + str(self.ubch) + \
            ' - ' + str(self.ubch.parish) + ' - ' +\
            str(self.ubch.parish.municipality) + \
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
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Relación con el modelo CommunalCouncil
    communal_council = models.ForeignKey(
        CommunalCouncil, on_delete=models.CASCADE,
        verbose_name='consejo comunal', null=True
    )

    # Relación con el modelo Profile
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, verbose_name='perfil', null=True
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre y apellido
        """

        return str(self.profile) + ' | ' + str(self.communal_council) + \
            ' - ' + str(self.communal_council.ubch.parish) + ' - ' +\
            str(self.communal_council.ubch.parish.municipality) + \
            ' - ' + str(self.communal_council.ubch.parish.municipality.estate)

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
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Relación con el modelo CommunityLeader
    community_leader = models.ForeignKey(
        CommunityLeader, on_delete=models.CASCADE,
        verbose_name='líder de comunidad'
    )

    # Relación con el modelo Profile
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, verbose_name='perfil', null=True
    )

    # Relación con el modelo Bridge
    bridge = models.OneToOneField(
        Bridge, on_delete=models.CASCADE, verbose_name='puente', null=True
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre y apellido
        """

        return str(self.profile) + ' | ' + str(self.community_leader)

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Líder de calle'
        verbose_name_plural = 'Líderes de calle'


class FamilyGroup(models.Model):
    """!
    Clase que contiene los datos de un usuario que gestiona su grupo familiar

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Relación con el modelo StreetLeader
    street_leader = models.ForeignKey(
        StreetLeader, on_delete=models.CASCADE, verbose_name='líder de calle'
    )

    # Relación con el modelo Profile
    profile = models.OneToOneField(
        Profile, on_delete=models.CASCADE, verbose_name='perfil'
    )

    # Relación con el modelo Department
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, verbose_name='departamento',
        null=True
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con el nombre y apellido
        """

        return str(self.profile) + ' | ' + str(self.street_leader)

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Grupo Familiar'
        verbose_name_plural = 'Grupos Familiares'
        ordering= [
            'department__building__bridge__block__name',
            'department__building__name',
            'department__name'
        ]


class Person(models.Model):
    """!
    Clase que contiene los datos principales de las personas

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Nombres
    first_name = models.CharField('nombres', max_length=100)

    # Apellidos
    last_name = models.CharField('apellidos', max_length=100)

    # Cédula de identidad
    id_number = models.CharField(
        'cédula de identidad', max_length=11, unique=True,
        validators=[
            validators.RegexValidator(
                r'^(([\d]{7}|[\d]{8})|([\d]{7}|[\d]{8})-([\d]{1}|[\d]{2}))$',
                'Introduzca una cédula de identidad válida'
            ),
        ]
    )

    # Correo electrónico
    email = models.CharField(
        'correo electrónico', max_length=100, null=True, blank=True
    )

    # Teléfono (04160000000)
    phone = models.CharField('teléfono', max_length=11, null=True, blank=True)

    # Fecha de nacimiento
    birthdate = models.DateField('fecha de nacimiento', blank=True, null=True)

    # Estalece si la persona es jefe familiar o no
    family_head = models.BooleanField('jefe de familia')

    # Fecha de ingreso
    admission_date = models.DateField('fecha de ingreso', blank=True, null=True)

    # Relación con el modelo Gender
    gender = models.ForeignKey(
        Gender, on_delete=models.CASCADE, verbose_name='género',
        null=True
    )

    # Relación con el modelo VoteType
    vote_type = models.ForeignKey(
        VoteType, on_delete=models.CASCADE, verbose_name='tipo de voto',
        null=True
    )

    # Relación con el modelo Relationship
    relationship = models.ForeignKey(
        Relationship, on_delete=models.CASCADE, verbose_name='parentesco',
        null=True
    )

    # Relación con el modelo FamilyGroup
    family_group = models.ForeignKey(
        FamilyGroup, on_delete=models.CASCADE, verbose_name='grupo familiar'
    )

    def age(self):
        """!
        Método que calcula la edad de la persona

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Retorna un número entero que representa la edad
        """

        if self.birthdate:
            return int((datetime.date.today() - self.birthdate).days / 365.25)
        return 0

    def living(self):
        """!
        Método que calcula tiempo viviendo en la residencia

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Retorna una tupla con los años y la edad
        """

        if self.admission_date:
            data = relativedelta(datetime.date.today(), self.admission_date)
            return (data.years, data.months)
        return (0, 0)

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con los nombres y apellidos
        """

        return self.first_name + ' ' + self.last_name + ' - ' + self.id_number

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = [
            'family_group__department__building__bridge__block__name',
            'family_group__department__building__name',
            'family_group__department__name'
        ]


class Admonition(models.Model):
    """!
    Clase que contiene las amonestaciones

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Fecha
    date = models.DateField('fecha')

    # Descripción
    description = models.TextField('descripción')

    # Relación con el modelo Person
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, verbose_name='persona',
    )

    # Relación con el modelo User
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='usuario', null=True,
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con los nombres y apellidos
        """

        return str(self.date)

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Amonestación'
        verbose_name_plural = 'Amonestaciones'


class MoveOut(models.Model):
    """!
    Clase que contiene las solicitudes de mudanzas

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Aprovado
    approved = models.BooleanField('aprovado', default=False)

    # Fecha
    date = models.DateField('fecha')

    # Descripción
    description = models.TextField('descripción', blank=True)

    # Líder de calle
    street_leader = models.CharField('líder de calle', max_length=100)

    # Datos de la persona
    person = models.CharField('persona', max_length=300)

    # Dirección de dónde se muda
    from_address = models.CharField('desde', max_length=200)

    # Dirección hacia donde se muda
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, verbose_name='departamento',
    )

    # Relación con el modelo User
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='usuario'
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con los nombres y apellidos
        """

        return str(self.person)

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Mudanza'
        verbose_name_plural = 'Mudanzas'


class Condominium(models.Model):
    """!
    Clase que contiene pagos del condominio

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Fecha
    date = models.DateField('fecha', unique=True, db_comment='Fecha')

    # Tasa del dólar
    rate = models.DecimalField(
        'tasa', max_digits=6, decimal_places=2, default=Decimal('0.00'),
        db_comment='Tasa del dólar'
    )

    # Monto en dólares
    amount = models.IntegerField(
        'monto', default=0, db_comment='Monto del condominio en dolares'
    )

    # Cierre de cuentas del condominio
    closing = models.BooleanField(
        'cierre', default=False, db_comment='Cierre de cuentas del condominio',
    )

    # Relación con el modelo User
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='usuario',
        db_comment='Relación con el modelo usuario'
    )

    def total_amount_bs(self):
        """!
        Método que calcula la suma de todos los pagos del conominio por departamento en bs

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Retorna un número entero que representa el total de pagos de condominios
        """

        sum = 0
        for payment in self.payment_set.all():
            for family_head in payment.familyhead_set.all():
                if family_head.paid and not family_head.exonerated:
                    sum = sum + family_head.amount
        return sum
    
    def total_amount_usd(self):
        """!
        Método que calcula la suma de todos los pagos del conominio por departamento en dólares

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return Retorna un número entero que representa el total de pagos de condominios
        """

        return self.total_amount_bs() / self.rate

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con fecha, tasa y monto
        """

        return str(self.date) + ' | ' + str(self.rate) + ' | ' + str(self.amount)

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        verbose_name = 'Condominio'
        verbose_name_plural = 'Condominios'
        ordering = ['-date']


class Payment(models.Model):
    """!
    Clase que contiene pagos del condominio por departamento

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Dirección del departamento
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, verbose_name='departamento', null=True,
        db_comment='Relación con el modelo departamento'
    )

    # Relación con el modelo Condominium
    condominium = models.ForeignKey(
        Condominium, on_delete=models.CASCADE, verbose_name='condominio',
        db_comment='Relación con el modelo condominio',
    )

    # Relación con el modelo User
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='usuario', null=True,
        db_comment='Relación con el modelo usuario',
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con los nombres y apellidos
        """

        return str(self.department)

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        ordering = [
            'department__building__bridge__block__name',
            'department__building__bridge__name',
            'department__building__name',
            'department__name',
        ]
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'


class FamilyHead(models.Model):
    """!
    Clase que contiene pagos del jefe de familia

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    # Nombres y apellidos del pagador
    payer = models.CharField(
        'pagador', max_length=200, db_comment='Nombre y apellido del Pagador',
    )

    # Cédula de identidad
    id_number = models.CharField(
        'cédula de identidad', max_length=11, null=True,
        db_comment='Cédula del Pagador',
    )

    # ¿Pagado?
    paid = models.BooleanField(
        '¿pagado?', default=True, db_comment='¿Pagado?',
    )

    # ¿Exonerado?
    exonerated = models.BooleanField(
        '¿exonerado?', default=False, db_comment='¿Pago exonerado?',
    )

    # Monto en bs del condominio (condominium.rate * condominium.amount) / total_family_group
    amount = models.DecimalField(
        'monto en bs del condominio', max_digits=10, decimal_places=2, default=Decimal('0.00'),
        db_comment='Monto en bs a pagar: (tasa del dolar * monto del condominio) / total familias',
    )

    # Descripción
    description = models.TextField(
        'Descripción', blank=True, db_comment='Descripción del pago',
    )

    # Relación con el modelo Payment
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, verbose_name='pago',
        db_comment='Relación con el modelo pago',
    )

    def __str__(self):
        """!
        Función para representar la clase de forma amigable

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @return string <b>{object}</b> Objeto con los nombres y apellidos
        """

        return self.payer

    class Meta:
        """!
        Meta clase del modelo que establece algunas propiedades

        @author William Páez (paez.william8 at gmail.com)
        """

        ordering = [
            'payment__department__building__bridge__block__name',
            'payment__department__building__bridge__name',
            'payment__department__building__name',
            'payment__department__name',
        ]
        verbose_name = 'Jefe de familia'
        verbose_name_plural = 'Jefes de familia'
