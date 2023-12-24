# Censo

Permite hacer un censo y luego exportarlo a un archivo excel

## Pasos para crear el entorno de desarrollo

Cuando somos un usuario normal del sistema, en el terminal se mostrará el siguiente símbolo: ~$

Cuando accedemos al usuario root del sistema, en el terminal se mostrará el siguiente símbolo: ~#

Probado en últimas versiones estables de Debian y Ubuntu. Instalar los siguientes programas

    ~# apt install curl git graphviz graphviz-dev phppgadmin postgresql python3-dev virtualenv

Para instalar npm hacer lo siguiente

    // Ubuntu
    ~$ curl -sL https://deb.nodesource.com/setup_lts.x | sudo -E bash -

    // Debian
    ~# curl -sL https://deb.nodesource.com/setup_lts.x | bash -

    ~# apt install -y nodejs

Crear las siguientes carpetas

    ~$ mkdir Programación

Desde el terminal, moverse a la carpeta Programación y ejecutar

    ~$ cd Programación/

    ~$ mkdir python

Entrar a la carpeta python y hacer lo siguiente

    ~$ cd python/

    ~$ mkdir entornos_virtuales proyectos_django

Entrar a entornos_virtuales

    ~$ cd entornos_virtuales/

    ~$ mkdir django

Desde el terminal, moverse a la carpeta django y ejecutar

    ~$ cd django/

    ~$ virtualenv -p python3 census

Para activar el entorno

    ~$ source census/bin/activate

Nos movemos a la carpeta proyectos_django, descargamos el sistema y entramos a la carpeta con los siguientes comandos

    (census) ~$ cd ../../proyectos_django/

    (census) ~$ git clone https://github.com/willez88/census.git

    (census) ~$ cd census/

    (census) ~$ cp census/settings.default.py census/settings.py

Tendremos las carpetas estructuradas de la siguiente manera

    // Entorno virtual
    Programación/python/entornos_virtuales/django/census

    // Servidor de desarrollo
    Programación/python/proyectos_django/census

Instalar las dependencias de css y js: moverse a la carpeta static y ejecutar

    (census) ~$ cd static/

    // Usa el archivo package.json para instalar lo que ya se configuro allí
    (census) ~$ npm install

    // Terminado el proceso volver a la carpeta raíz del proyecto
    (census) ~$ cd ../

Crear la base de datos para __census__ usando PostgresSQL

    // Acceso al usuario postgres
    ~# su postgres

    // Acceso a la interfaz de comandos de PostgreSQL
    postgres@xxx:$ psql

    // Creación del usuario de a base de datos
    postgres=# CREATE USER admin WITH LOGIN ENCRYPTED PASSWORD '123' CREATEDB;
    postgres=# \q

    // Desautenticar el usuario PostgreSQL y regresar al usuario root
    postgres@xxx:$ exit

    // Salir del usuario root
    ~# exit

Puedes crear la base de datos colocando en el navegador: localhost/phppgadmin

    // Nombre de la base de datos: census

Instalamos los requemientos que el sistema necesita en el entorno virtual

    (census) ~$ pip install -r requirements/dev.txt

Hacer las migraciones

    (census) ~$ python manage.py makemigrations base user

    (census) ~$ python manage.py migrate

    (census) ~$ python manage.py loaddata auth_group 1_country 2_estate 3_municipality 4_parish 1_ubch 2_communal_council 3_block 4_bridge 5_building 6_department gender relationship vote_type

Crear usuario administrador

    (census) ~$ python manage.py createsuperuser

Correr el servidor de django

    (census) ~$ python manage.py runserver

Poner en el navegador la url que sale en el terminal para entrar el sistema

Llegado hasta aquí el sistema ya debe estar funcionando

Para salir del entorno virtual se puede ejecutar desde cualquier lugar del terminal: deactivate

Generar gráfico del modelo Entidad-Relación

    // Grafica el modelo entidad-relación del proyecto
    (census) ~$ python manage.py graph_models -a -g -o census.svg

    // Grafica el modelo de una app del proyecto
    (census) ~$ python manage.py graph_models base -g -o base.svg

Estilo de codificación PEP 8 en Visual Studio Code

    // Abre el proyecto con vscode
    (census) ~$ code .

    Ir a extensiones del vscode e instalar
        ruff
        isort
        Python Environment Manager

    Python Environment Manager detectará todos los entornos virtuales creados
    en la sección Venv, click en "Set as active workspace interpreter" para activarlo

    Para que los cambios hagan efecto cerrar el vscode y abrirlo de nuevo

Exportar base de datos usando Django

    // Respaldo completo de los datos
    (census) ~$ python manage.py dumpdata --indent 4 > db/census_prod.json

Importar base de datos usando Django

    // Resetear base de datos
    (census) ~$ python manage.py reset_db

    // Eliminar las migraciones del proyecto
    (census) ~$ find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

    // Eliminar los archivos compilados
    (census) ~$ python manage.py clean_pyc

    // Ejecutar
    (census) ~$ python manage.py makemigrations base user
    
    (census) ~$ python manage.py migrate

    // Luego entrar al gestor de base de datos
    //conectarse a la base de datos census
    postgres=# \c census

    // Vaciar las siguientes tablas para que no generen conflicto cuando se importen los datos
    census=# TRUNCATE TABLE auth_permission CASCADE;
    census=# TRUNCATE TABLE django_content_type CASCADE;

    // Por último importar census_prod.json
    (census) ~$ python manage.py loaddata db/census_prod.json
