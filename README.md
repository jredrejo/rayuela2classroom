rayuela2classroom

=================

Script para exportar los usuarios de Rayuela a un archivo csv aceptado por Google Apps para dar de alta de forma masiva a los usuarios de un grupo de alumnos


INSTRUCCIONES:
- Obtener de Rayuela el archivo de exportación de los alumnos que se usa para darlos de alta en el servidor del centro.
- Si es un archivo zip, extraer el archivo Alumnos.xml que está dentro de este archivo.
- Sintáxis:

    Rayuela2CSV.py *[-a]* ruta_al_archivo_Alumnos.xml

  - Si se añade el argumento opcional **-a**, p. ej.
        ```bash
        ./Rayuela2CSV.py -a /tmp/Alumnos.xml
        ```
        el programa generará un archivo csv, con el nombre salida_NombreGrupo.csv por cada uno de los grupos que haya en el fichero de Alumnos.

  - Si no se usa el argumento *-a*, el programa mostrará la lista de grupos disponibles y solicita que se introduzca el nombre del grupo del que se desea dar de alta a los alumnos.
  - Una vez introducido el nombre el programa genera un archivo llamado "salida.csv" en el mismo directorio donde se haya ejecutado Rayuela2CSV.
  
  
- Los archivos de extensión .csv generados se usan en la consola de administración de Google Apps para dar de alta masivamente a estos alumnos. En este archivo se encuentra el correo creado al usuario y su contraseña. Es muy recomendable activar la opción de que deban cambiar la contraseña la primera vez que entren en la plataforma.
- Este mismo archivo .csv se puede proporcionar al profesor del grupo para que comunique su cuenta de correo y usuario a sus alumnos.
