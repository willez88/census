import datetime

from django.conf import settings
from django.http import (
    HttpResponse,
    JsonResponse,
)
from django.shortcuts import redirect
from django.views.generic import (
    TemplateView,
    View,
)
from openpyxl import Workbook
from openpyxl.styles import (
    Alignment,
    Font,
    PatternFill,
)
from openpyxl.writer.excel import save_virtual_workbook
from user.models import (
    CommunityLeader,
    FamilyGroup,
    Person,
    StreetLeader
)

from .models import (
    Building,
    Department,
    Relationship,
    VoteType
)


class HomeView(TemplateView):
    """!
    Clase que muestra la página inicial

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    template_name = 'base/base.html'


class Error403View(TemplateView):
    """!
    Clase que muestra la página de error de permisos

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    template_name = 'base/error_403.html'


class ExportExcelView(View):
    """!
    Clase que descarga datos relacionados a los usuarios Líder de Comunidad

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-3.0.html'>
        GNU Public License versión 3 (GPLv3)</a>
    """

    def dispatch(self, request, *args, **kwargs):
        """!
        Función que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene los datos de la
            petición
        @param *args <b>{tuple}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return super <b>{object}</b> Entra a la vista correspondiente
            sino redirecciona hacia la vista de error de permisos
        """

        if self.request.user.groups.filter(name='Líder de Comunidad'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get(self, request, *args, **kwargs):
        """!
        Función que descarga un archivo excel

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Retorna datos en un archivo excel
        """

        workbook = Workbook()
        worksheet1 = workbook.active
        worksheet1.title = 'Hoja 1'
        worksheet1.merge_cells('A1:H1')
        worksheet1.merge_cells('A2:H2')
        worksheet1.merge_cells('A3:H3')
        worksheet1.column_dimensions['A'].width = 20
        worksheet1[
            'A1'
        ] = 'VICEPRESIDENCIA TERRITORIAL PSUV ESTADOS MÉRIDA - TRUJILLO'
        worksheet1['A1'].font = Font(color='FF0000')
        worksheet1['A2'] = 'EQUIPO POLÍTICO ESTADAL PSUV MÉRIDA'
        worksheet1['A2'].font = Font(color='FF0000')
        worksheet1['A3'] = 'COMISIÓN DE ORGANIZACIÓN PSUV MÉRIDA'
        worksheet1['A3'].font = Font(color='FF0000')
        worksheet1['A6'] = 'CENSO RAAS'

        date = datetime.datetime.now()
        worksheet1['A8'] = 'FECHA DE ACTUALIZACIÓN: ' + '%s-%s-%s %s-%s Hrs' %\
            (date.day, date.month, date.year, date.hour, date.minute)

        community_leader = CommunityLeader.objects.get(
            profile=self.request.user.profile
        )
        worksheet1['A10'] = 'Municipio:'
        worksheet1[
            'B10'
        ] = str(community_leader.communal_council.ubch.parish.municipality)

        worksheet1['A11'] = 'Parroquia:'
        worksheet1['B11'] = str(community_leader.communal_council.ubch.parish)

        worksheet1['A12'] = 'Código UBCH:'
        worksheet1['B12'] = community_leader.communal_council.ubch.code

        worksheet1['A13'] = 'Nombre UBCH:'
        worksheet1['B13'] = community_leader.communal_council.ubch.name

        worksheet1['A14'] = 'Código Comunidad:'

        worksheet1['A15'] = 'Nombre Comunidad:'
        worksheet1['B15'] = community_leader.communal_council.name

        worksheet1['A17'] = 'Calles Registradas:'
        worksheet1['B17'] = str(len(StreetLeader.objects.filter(
            community_leader=community_leader))
        )

        # Hojas con los censos
        i = 2
        for street_leader in StreetLeader.objects.filter(
            community_leader=community_leader
        ):
            worksheet = workbook.create_sheet(title='Hoja ' + str(i))
            worksheet.merge_cells('A1:H1')
            worksheet.merge_cells('A2:H2')
            worksheet.merge_cells('A3:H3')
            worksheet.column_dimensions['A'].width = 16
            worksheet.column_dimensions['B'].width = 25
            worksheet.column_dimensions['C'].width = 16
            worksheet.column_dimensions['D'].width = 25
            worksheet.column_dimensions['E'].width = 20
            worksheet.column_dimensions['F'].width = 20
            worksheet.column_dimensions['G'].width = 20
            worksheet[
                'A1'
            ] = 'VICEPRESIDENCIA TERRITORIAL PSUV ESTADOS MÉRIDA - TRUJILLO'
            worksheet['A1'].font = Font(color='FF0000')
            worksheet['A2'] = 'EQUIPO POLÍTICO ESTADAL PSUV MÉRIDA'
            worksheet['A2'].font = Font(color='FF0000')
            worksheet['A3'] = 'COMISIÓN DE ORGANIZACIÓN PSUV MÉRIDA'
            worksheet['A3'].font = Font(color='FF0000')
            worksheet['A6'] = 'CENSO CALLE RAAS'

            date = datetime.datetime.now()
            worksheet[
                'A8'
            ] = 'FECHA DE ACTUALIZACIÓN: ' + '%s-%s-%s %s-%s Hrs' % \
                (date.day, date.month, date.year, date.hour, date.minute)

            community_leader = CommunityLeader.objects.get(
                profile=self.request.user.profile
            )
            worksheet['A10'] = 'Municipio:'
            worksheet[
                'B10'
            ] = str(community_leader.communal_council.ubch.parish.municipality)

            worksheet['A11'] = 'Parroquia:'
            worksheet[
                'B11'
            ] = str(community_leader.communal_council.ubch.parish)

            worksheet['A12'] = 'Código UBCH:'
            worksheet['B12'] = community_leader.communal_council.ubch.code

            worksheet['A13'] = 'Nombre UBCH:'
            worksheet['B13'] = community_leader.communal_council.ubch.name

            worksheet['A14'] = 'Código Comunidad:'

            worksheet['A15'] = 'Nombre Comunidad:'
            worksheet['B15'] = community_leader.communal_council.name

            worksheet['A16'] = 'Lider de Calle:'
            worksheet['B16'] = str(street_leader.profile)

            worksheet.merge_cells('A19:H19')
            worksheet.merge_cells('A20:H20')
            worksheet['A19'] = 'CENSO REGISTRADO'
            worksheet['A19'].alignment = Alignment(horizontal='center')
            worksheet['A20'] = 'NOTA: TIPO DE VOTOS PERMITIDOS: DURO, BLANDO, \
                OPOSITOR | ESTATUS DE CONTACTADO: SI O NO | JEFE DE FAMILIA: \
                SI O NO | RECIBIÓ CLAP EN LOS ÚLTIMOS TRES MESES: SI O NO'

            worksheet[
                'A21'
            ].fill = PatternFill(start_color='FF0000', fill_type='solid')
            worksheet['A21'].font = Font(color='FFFFFF')
            worksheet['A21'].alignment = Alignment(horizontal='center')

            worksheet[
                'B21'
            ].fill = PatternFill(start_color='FF0000', fill_type='solid')
            worksheet['B21'].font = Font(color='FFFFFF')
            worksheet['B21'].alignment = Alignment(horizontal='center')

            worksheet[
                'C21'
            ].fill = PatternFill(start_color='FF0000', fill_type='solid')
            worksheet['C21'].font = Font(color='FFFFFF')
            worksheet['C21'].alignment = Alignment(horizontal='center')

            worksheet[
                'D21'
            ].fill = PatternFill(start_color='FF0000', fill_type='solid')
            worksheet['D21'].font = Font(color='FFFFFF')
            worksheet['D21'].alignment = Alignment(horizontal='center')

            worksheet[
                'E21'
            ].fill = PatternFill(start_color='FF0000', fill_type='solid')
            worksheet['E21'].font = Font(color='FFFFFF')
            worksheet['E21'].alignment = Alignment(horizontal='center')

            worksheet[
                'F21'
            ].fill = PatternFill(start_color='FF0000', fill_type='solid')
            worksheet['F21'].font = Font(color='FFFFFF')
            worksheet['F21'].alignment = Alignment(horizontal='center')

            worksheet[
                'G21'
            ].fill = PatternFill(start_color='FF0000', fill_type='solid')
            worksheet['G21'].font = Font(color='FFFFFF')
            worksheet['G21'].alignment = Alignment(horizontal='center')

            worksheet['A21'] = 'CÉDULA'
            worksheet['B21'] = 'NOMBRES Y APELLIDOS'
            worksheet['C21'] = 'TELÉFONO'
            worksheet['D21'] = 'Correo'
            worksheet['E21'] = 'TIPO DE VOTO'
            worksheet['F21'] = 'PARENTESCO'
            worksheet['G21'] = 'ES JEFE DE FAMILIA'
            c = 22
            for family_group in FamilyGroup.objects.filter(
                street_leader=street_leader
            ):
                # print(Person.objects.filter(family_group=family_group))
                for person in Person.objects.filter(family_group=family_group):
                    column1 = 'A'+str(c)
                    worksheet[column1] = person.id_number

                    column2 = 'B'+str(c)
                    worksheet[
                        column2
                    ] = person.first_name + ' ' + person.last_name

                    column3 = 'C'+str(c)
                    worksheet[column3] = person.phone

                    column4 = 'D'+str(c)
                    worksheet[column4] = person.email

                    column5 = 'E'+str(c)
                    worksheet[column5] = str(person.vote_type)

                    column6 = 'F'+str(c)
                    worksheet[column6] = str(person.relationship)

                    column7 = 'G'+str(c)
                    if person.family_head:
                        worksheet[column7] = 'SI'
                    else:
                        worksheet[column7] = 'No'

                    c = c + 1

                column8 = 'A'+str(c)
                worksheet[column8] = ' '
                c = c + 1

            i = i + 1

        response = HttpResponse(
            content=save_virtual_workbook(workbook),
            content_type='application/ms-excel'
        )
        response['Content-Disposition'] = 'attachment; filename="data.xlsx"'
        # response.write(u'\ufeff'.encode('utf8'))
        return response


class ExportExcelStreetLeaderView(View):
    """!
    Clase que descarga datos relacionados a los usuarios Líder de Calle

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-3.0.html'>
        GNU Public License versión 3 (GPLv3)</a>
    """

    def dispatch(self, request, *args, **kwargs):
        """!
        Función que valida si el usuario del sistema tiene permisos para entrar
        a esta vista

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene los datos de la
            petición
        @param *args <b>{tuple}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return super <b>{object}</b> Entra a la vista correspondiente
            sino redirecciona hacia la vista de error de permisos
        """

        if self.request.user.groups.filter(name='Líder de Calle'):
            return super().dispatch(request, *args, **kwargs)
        return redirect('base:error_403')

    def get(self, request, *args, **kwargs):
        """!
        Función que descarga un archivo excel

        @author William Páez (paez.william8 at gmail.com)
        @param self <b>{object}</b> Objeto que instancia la clase
        @param request <b>{object}</b> Objeto que contiene la petición
        @param *args <b>{tupla}</b> Tupla de valores, inicialmente vacia
        @param **kwargs <b>{dict}</b> Diccionario de datos, inicialmente vacio
        @return Retorna datos en un archivo excel
        """

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'Hoja 1'
        worksheet.merge_cells('A1:H1')
        worksheet.merge_cells('A2:H2')
        worksheet.merge_cells('A3:H3')
        worksheet.column_dimensions['A'].width = 16
        worksheet.column_dimensions['B'].width = 25
        worksheet.column_dimensions['C'].width = 16
        worksheet.column_dimensions['D'].width = 25
        worksheet.column_dimensions['E'].width = 20
        worksheet.column_dimensions['F'].width = 20
        worksheet.column_dimensions['G'].width = 20
        worksheet[
            'A1'
        ] = 'VICEPRESIDENCIA TERRITORIAL PSUV ESTADOS MÉRIDA - TRUJILLO'
        worksheet['A1'].font = Font(color='FF0000')
        worksheet['A2'] = 'EQUIPO POLÍTICO ESTADAL PSUV MÉRIDA'
        worksheet['A2'].font = Font(color='FF0000')
        worksheet['A3'] = 'COMISIÓN DE ORGANIZACIÓN PSUV MÉRIDA'
        worksheet['A3'].font = Font(color='FF0000')
        worksheet['A6'] = 'CENSO CALLE RAAS'

        date = datetime.datetime.now()
        worksheet[
            'A8'
        ] = 'FECHA DE ACTUALIZACIÓN: ' + '%s-%s-%s %s-%s Hrs' % \
            (date.day, date.month, date.year, date.hour, date.minute)

        street_leader = StreetLeader.objects.get(
            profile=self.request.user.profile
        )
        community_leader = street_leader.community_leader
        worksheet['A10'] = 'Municipio:'
        worksheet[
            'B10'
        ] = str(community_leader.communal_council.ubch.parish.municipality)

        worksheet['A11'] = 'Parroquia:'
        worksheet[
            'B11'
        ] = str(community_leader.communal_council.ubch.parish)

        worksheet['A12'] = 'Código UBCH:'
        worksheet['B12'] = community_leader.communal_council.ubch.code

        worksheet['A13'] = 'Nombre UBCH:'
        worksheet['B13'] = community_leader.communal_council.ubch.name

        worksheet['A14'] = 'Código Comunidad:'

        worksheet['A15'] = 'Nombre Comunidad:'
        worksheet['B15'] = community_leader.communal_council.name

        worksheet['A16'] = 'Lider de Calle:'
        worksheet['B16'] = str(street_leader.profile)

        worksheet.merge_cells('A19:H19')
        worksheet.merge_cells('A20:H20')
        worksheet['A19'] = 'CENSO REGISTRADO'
        worksheet['A19'].alignment = Alignment(horizontal='center')
        worksheet['A20'] = 'NOTA: TIPO DE VOTOS PERMITIDOS: DURO, BLANDO, \
                OPOSITOR | ESTATUS DE CONTACTADO: SI O NO | JEFE DE FAMILIA: \
                SI O NO | RECIBIÓ CLAP EN LOS ÚLTIMOS TRES MESES: SI O NO'

        worksheet[
            'A21'
        ].fill = PatternFill(start_color='FF0000', fill_type='solid')
        worksheet['A21'].font = Font(color='FFFFFF')
        worksheet['A21'].alignment = Alignment(horizontal='center')

        worksheet[
            'B21'
        ].fill = PatternFill(start_color='FF0000', fill_type='solid')
        worksheet['B21'].font = Font(color='FFFFFF')
        worksheet['B21'].alignment = Alignment(horizontal='center')

        worksheet[
            'C21'
        ].fill = PatternFill(start_color='FF0000', fill_type='solid')
        worksheet['C21'].font = Font(color='FFFFFF')
        worksheet['C21'].alignment = Alignment(horizontal='center')

        worksheet[
            'D21'
        ].fill = PatternFill(start_color='FF0000', fill_type='solid')
        worksheet['D21'].font = Font(color='FFFFFF')
        worksheet['D21'].alignment = Alignment(horizontal='center')

        worksheet[
            'E21'
        ].fill = PatternFill(start_color='FF0000', fill_type='solid')
        worksheet['E21'].font = Font(color='FFFFFF')
        worksheet['E21'].alignment = Alignment(horizontal='center')

        worksheet[
            'F21'
        ].fill = PatternFill(start_color='FF0000', fill_type='solid')
        worksheet['F21'].font = Font(color='FFFFFF')
        worksheet['F21'].alignment = Alignment(horizontal='center')

        worksheet[
            'G21'
        ].fill = PatternFill(start_color='FF0000', fill_type='solid')
        worksheet['G21'].font = Font(color='FFFFFF')
        worksheet['G21'].alignment = Alignment(horizontal='center')

        worksheet['A21'] = 'CÉDULA'
        worksheet['B21'] = 'NOMBRES Y APELLIDOS'
        worksheet['C21'] = 'TELÉFONO'
        worksheet['D21'] = 'Correo'
        worksheet['E21'] = 'TIPO DE VOTO'
        worksheet['F21'] = 'PARENTESCO'
        worksheet['G21'] = 'ES JEFE DE FAMILIA'
        c = 22
        for family_group in FamilyGroup.objects.filter(
            street_leader=street_leader
        ):
            for person in Person.objects.filter(family_group=family_group):
                column1 = 'A'+str(c)
                worksheet[column1] = person.id_number

                column2 = 'B'+str(c)
                worksheet[
                    column2
                ] = person.first_name + ' ' + person.last_name

                column3 = 'C'+str(c)
                worksheet[column3] = person.phone

                column4 = 'D'+str(c)
                worksheet[column4] = person.email

                column5 = 'E'+str(c)
                worksheet[column5] = str(person.vote_type)

                column6 = 'F'+str(c)
                worksheet[column6] = str(person.relationship)

                column7 = 'G'+str(c)
                if person.family_head:
                    worksheet[column7] = 'SI'
                else:
                    worksheet[column7] = 'No'

                c = c + 1

            column8 = 'A'+str(c)
            worksheet[column8] = ' '
            c = c + 1

        response = HttpResponse(
            content=save_virtual_workbook(workbook),
            content_type='application/ms-excel'
        )
        response['Content-Disposition'] = 'attachment; filename="data.xlsx"'
        return response


class VoteTypeListView(View):
    """!
    Clase que retorna un json con los datos de tipos de voto

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def get(self, request, *args, **kwargs):
        vote_types = VoteType.objects.all()
        vote_type_list = []
        vote_type_list.append({
            'id': '', 'text': 'Seleccione...'
        })
        for vote_type in vote_types:
            vote_type_list.append({
                'id': vote_type.id, 'text': vote_type.name
            })
        return JsonResponse(
            {'status': 'true', 'list': vote_type_list}, status=200
        )


class RelationshipListView(View):
    """!
    Clase que retorna un json con los datos de parentescos

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def get(self, request, *args, **kwargs):
        relationships = Relationship.objects.all()
        relationship_list = []
        relationship_list.append({
            'id': '', 'text': 'Seleccione...'
        })
        for relationship in relationships:
            relationship_list.append({
                'id': relationship.id, 'text': relationship.name
            })
        return JsonResponse(
            {'status': 'true', 'list': relationship_list}, status=200
        )


class BuildingListView(View):
    """!
    Clase que retorna un json con los datos de edificios

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def get(self, request, *args, **kwargs):
        profile = self.request.user.profile
        street_leader = StreetLeader.objects.get(profile=profile)
        buildings = Building.objects.filter(bridge=street_leader.bridge)
        building_list = []
        building_list.append({
            'id': '', 'text': 'Seleccione...'
        })
        for building in buildings:
            building_list.append({
                'id': building.id, 'text': building.name
            })
        return JsonResponse(
            {'status': 'true', 'list': building_list}, status=200
        )


class DepartmentListView(View):
    """!
    Clase que retorna un json con los datos de departamentos

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def get(self, request, *args, **kwargs):
        departments = Department.objects.all()
        department_list = []
        department_list.append({
            'id': '', 'text': 'Seleccione...'
        })
        for department in departments:
            department_list.append({
                'id': department.id, 'text': department.name
            })
        return JsonResponse(
            {'status': 'true', 'list': department_list}, status=200
        )


class GetDepartmentView(View):
    """!
    Clase que retorna un json con los datos de un departamento

    @author William Páez (paez.william8 at gmail.com)
    @copyright <a href='http://www.gnu.org/licenses/gpl-2.0.html'>
        GNU Public License versión 2 (GPLv2)</a>
    """

    def get(self, request, *args, **kwargs):
        """!
        Retorna el json de departamentos filtrados por edificio

        @author William Páez (paez.william8 at gmail.com)
        """

        building = Building.objects.get(pk=self.kwargs['building_id'])
        departments = Department.objects.filter(building=building)
        department_list = []
        department_list.append({
            'id': '', 'text': 'Seleccione...'
        })
        for department in departments:
            department_list.append({
                'id': department.id, 'text': department.name
            })
        return JsonResponse(
            {'status': 'true', 'list': department_list}, status=200
        )
