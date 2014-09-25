#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# #############################################################################
# Project:     ControlIES
# Module:      Rayuela2Classroom.py
# Purpose:     Create csv file to export Rayuela data into Google Classroom
# Language:    Python 2.7
# Date:        20-Sep-2014.
# Ver:         20-Sep-2014.
# Author:   José L. Redrejo Rodríguez
# Copyright:    2014 - José L. Redrejo Rodríguez <jredrejo @no-spam@ debian.org>
#
#
# This script is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This script is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this script. If not, see <http://www.gnu.org/licenses/>.
#
# #############################################################################

import os
import sys
import xml.dom.minidom


class Users(object):
    def __init__(self, name, surname, nif, user, password, password2, classrooms):
        self.type = type
        self.name = name
        self.surname = surname
        self.nif = nif
        self.user = user
        self.password = password
        self.password2 = password2
        self.classrooms = classrooms
        if self.classrooms.__class__.__name__ == 'str': self.classrooms = [classrooms]


class Rayuela(object):
    def __init__(self, archivo):
        self.usuarios = []
        self.dni_usuarios = []
        self.logins = {}
        self.archivo = archivo
        self.aulas = {}



    def asegura_codigos(self, cadena):
        """Quita caracteres no válidos para los nombres de login
        de los usuarios"""
        resultado = cadena.replace(u"á", u"a")
        resultado = resultado.replace(u"Á", u"A")
        resultado = resultado.replace(u"à", u"a")
        resultado = resultado.replace(u"ä", u"a")
        resultado = resultado.replace(u"À", u"A")
        resultado = resultado.replace(u"Ä", u"A")
        resultado = resultado.replace(u"é", u"e")
        resultado = resultado.replace(u"ë", u"e")
        resultado = resultado.replace(u"É", u"E")
        resultado = resultado.replace(u"Ë", u"E")
        resultado = resultado.replace(u"è", u"e")
        resultado = resultado.replace(u"È", u"E")
        resultado = resultado.replace(u"í", u"i")
        resultado = resultado.replace(u"Í", u"I")
        resultado = resultado.replace(u"ì", u"i")
        resultado = resultado.replace(u"ï", u"i")
        resultado = resultado.replace(u"Ì", u"I")
        resultado = resultado.replace(u"Ï", u"I")
        resultado = resultado.replace(u"ó", u"o")
        resultado = resultado.replace(u"Ó", u"O")
        resultado = resultado.replace(u"Ö", u"O")
        resultado = resultado.replace(u"ò", u"o")
        resultado = resultado.replace(u"ö", u"o")
        resultado = resultado.replace(u"Ò", u"O")
        resultado = resultado.replace(u"ú", u"u")
        resultado = resultado.replace(u"Ú", u"U")
        resultado = resultado.replace(u"ü", u"u")
        resultado = resultado.replace(u"Ü", u"U")
        resultado = resultado.replace(u"ù", u"u")
        resultado = resultado.replace(u"Ù", u"U")
        resultado = resultado.replace(u"ª", u"a")
        resultado = resultado.replace(u"º", u"o")
        resultado = resultado.replace(u"ñ", u"n")
        resultado = resultado.replace(u"Ñ", u"N")
        resultado = resultado.replace(u"ç", u"c")
        resultado = resultado.replace(u"(", u"")
        resultado = resultado.replace(u")", u"")
        resultado = resultado.replace(u".", u"")
        resultado = resultado.replace(u",", u"")
        resultado = resultado.replace(u"&", u"")
        return str(resultado).strip()


    def chk_username(self, login, keep=False):
        """Comprueba si el login existe ya en la base de datos
        de ldap, y si existe le va aumentando el número del final"""
        if not keep:
            nuevo_login = login + "01"
        else:
            nuevo_login = login

        if nuevo_login not in self.logins.keys():
            return nuevo_login
        else:
            i = 2
            while nuevo_login in self.logins.keys():
                nuevo_login = login + "%02d" % (i)
                i += 1
            return nuevo_login

    def crea_logins(self):
        """Revisa la lista de usuarios y le asigna nuevo login al que
        no está ya en ldap o no lo trae de Rayuela"""

        for usuario in self.usuarios:
            usuario["nuevo"] = True
            if "dni" in usuario.keys():
                #contraseña del usuario:

                usuario["passwd"] = usuario["fecha-nacimiento"].replace("/", "")
                if usuario["passwd"] == "": usuario["passwd"] = usuario["dni"]

                if usuario["datos-usuario-rayuela"] != "false":  #esta en rayuela  su login
                    # en Rayuela no están validando los logins, lo que provoca que pueda haber
                    # logins no validos. Así que nos toca hacerlo a nosotros:
                    login_rayuela = self.asegura_codigos(usuario["datos-usuario-rayuela"])
                    login_rayuela = login_rayuela.lower().replace("-", "").replace(" ", "")
                    usuario["login"] = self.chk_username(login_rayuela, True)

                else:  #iniciales del nombre + primer apellido + inicial segundo apellido
                    login = ''
                    for i in zip(*usuario["nombre"].lower().split(" "))[0]:
                        login += i.strip()
                    for i in usuario["primer-apellido"].lower().replace("-", " ").split(" "):
                        login += i.strip()
                    if "segundo-apellido" in usuario.keys():
                        if len(usuario["segundo-apellido"]) > 0:
                            login += usuario["segundo-apellido"][0].lower().strip()
                    usuario["login"] = self.chk_username(login)
                self.logins[usuario["login"]] = usuario

            else:  #sin nie ni dni, no podemos gestionarlo
                self.usuarios.remove(usuario)


    def parse_nodo(self, nodo):
        """ para cada nodo en el xml, obtiene sus datos y prepara sus grupos"""
        usuario = {}

        for info in nodo.childNodes:
            if info.nodeType != info.TEXT_NODE:
                if info.nodeName in ("datos-usuario-rayuela", "foto", "grupos"):

                    dato = info.childNodes[1].firstChild.nodeValue
                    if info.nodeName == "foto" and dato == "true":
                        dato = info.getElementsByTagName("nombre-fichero")[0].firstChild.nodeValue
                    if info.nodeName == "datos-usuario-rayuela" and dato == "true":
                        dato = info.getElementsByTagName("login")[0].firstChild.nodeValue

                else:
                    try:
                        dato = info.firstChild.nodeValue
                    except:  # no hay dato en este nodo, p. ej. segundo-apellido
                        dato = ' '
                if info.nodeName == 'nie':
                    usuario["dni"] = self.asegura_codigos(dato)
                elif info.nodeName == 'grupo':  #no paso asegura_codigos para no quitar el "."
                    nombre_grupo = self.asegura_codigos(dato).replace(" ", "")
                    if len(nombre_grupo) > 0:
                        usuario['grupo'] = nombre_grupo

                else:
                    usuario[info.nodeName] = self.asegura_codigos(dato)

        self.usuarios.append(usuario)
        self.dni_usuarios.append(usuario["dni"])


    def parsea_archivo(self, archivo_xml):
        """Recorre el archivo xml y va generando la lista de usuarios"""

        xml_usuarios = xml.dom.minidom.parse(archivo_xml)
        lista = xml_usuarios.getElementsByTagName("alumno")

        for nodo in lista:
            self.parse_nodo(nodo)

        self.crea_logins()


    def lista_grupos(self, lista, clave, sin_grupo="SIN_AULA"):
        """Devuelve una enumeración de los grupos que pertenecen a
        clave, siendo normalmente clave igual a aulas o dptos"""
        grupos = {}

        for i in lista:
            if clave not in i.keys():
                grupo = sin_grupo
            else:
                grupo = i[clave]

            if grupo not in grupos.keys():
                grupos[grupo] = [i["login"]]
            else:
                grupos[grupo].append(i["login"])

        return grupos


    def crea_usuarios(self):
        """Da de alta en ldap los usuarios que están en el listado"""
        lista = []

        for usuario in self.usuarios:
            surname = usuario['primer-apellido'] + ' ' + usuario['segundo-apellido']
            nuevo = Users(usuario['nombre'], surname.strip(),
                          usuario['dni'], usuario['login'], usuario['passwd'], usuario['passwd'], '')
            lista.append((usuario['login'], usuario['passwd'], usuario['nombre'], surname))

        return lista


    def gestiona_archivo(self):
        """Función principal que a partir del archivo hace todo en ldap"""
        self.parsea_archivo(self.archivo)
        self.aulas = self.lista_grupos(self.usuarios, "grupo")
        total = self.crea_usuarios()
        return (total, self.aulas)

    def usuarios_grupo(self, grupo):
        import csv
        myfile = open('salida.csv', 'wb')
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        wr.writerow("First Name,Last Name,Email Address,Password".split(","))
        for usuario in self.aulas[grupo]:
            datos=self.logins[usuario]
            surname = datos['primer-apellido'] + ' ' + datos['segundo-apellido']
            wr.writerow([datos['nombre'],surname,"%s@santiagoapostol.net" % datos['login'],datos['passwd']])


if __name__ == '__main__':
    archivo = sys.argv[1]
    rayuela = Rayuela(archivo)
    todos = rayuela.gestiona_archivo()

    print "Esta es la lista de grupos, escribe el que deseas generar:"
    print todos[1].keys()
    grupo = raw_input()
    if grupo not in todos[1]:
        print "error en el nombre del grupo"
        sys.exit(1)
    else:
        rayuela.usuarios_grupo(grupo)
