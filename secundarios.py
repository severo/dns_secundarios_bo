#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import print_function
import argparse
import dns.name
import dns.resolver
import pyasn
import json

# Initialize module and load IP to ASN database
# the sample database can be downloaded or built - see below
asndb = pyasn.pyasn('rib.txt')

def buscar_asn_ipv4(ipv4):
    try:
        respuesta = asndb.lookup(ipv4)
    except:
        respuesta = ""
    return str(respuesta[0])

def buscar_lista_ipv4(d):
    try:
        respuestas = [r.to_text() for r in dns.resolver.query(d, 'A')]
    except:
        respuestas = []
    return respuestas

def buscar_lista_NS(d):
    try:
        respuestas = [r.to_text() for r in dns.resolver.query(d, 'NS')]
    except:
        respuestas = []
    return respuestas


# Construir un JSON con la siguiente estructura
#
# {
#   "dominio": "aduana.gob.bo",
#   "servidores_NS": [
#     {
#       "dominio": "bl-anb-4.aduana.gob.bo.",
#       "direcciones_ipv4": [
#         {
#           "ipv4": "190.129.75.197",
#           "asn": "6568"
#         }
#       ]
#     }
#   ]
# }
#
def buscar_servidores_autoridad(dominio):
    datos = {'dominio': dominio, 'servidores_NS': [], 'solo_dominios': [], 'solo_ipv4': [], 'solo_asn': []}

    # Consulta clave "NS"
    lista_NS = buscar_lista_NS(dominio)
    for NS in lista_NS:
        servidor_NS = {'dominio': NS, 'direcciones_ipv4': []}
        lista_ipv4 = buscar_lista_ipv4(NS)
        for ipv4 in lista_ipv4:
            asn = buscar_asn_ipv4(ipv4)
            servidor_NS['direcciones_ipv4'].append({'ipv4': ipv4, 'asn': asn})
            datos['solo_ipv4'].append(ipv4)
            datos['solo_asn'].append(asn)
        datos['servidores_NS'].append(servidor_NS)
        datos['solo_dominios'].append(NS)

    return datos

def preparar_tabla_formato(datos):
    tabla = [['Dominio','Servidor','IPv4','ASN']]
    dominio = datos['dominio']
    for s in datos['servidores_NS']:
        ns = s['dominio']
        for d in s['direcciones_ipv4']:
            ipv4 = d['ipv4']
            asn = d['asn']
            tabla.append([dominio, ns, ipv4, asn])
    return tabla

def formatear_stats(datos):
    dominio = datos['dominio']
    no_servidores = len(set(datos['solo_dominios']))
    no_ipv4 = len(set(datos['solo_ipv4']))
    no_asn = len(set(datos['solo_asn']))
    tabla = [dominio, no_servidores, no_ipv4, no_asn]

    print(*tabla, sep='\t')

def formatear_csv(tabla):
    tabla = preparar_tabla_formato(datos)

    for fila in tabla:
        print(*fila, sep='\t')

def formatear_pretty_print(tabla):
    tabla = preparar_tabla_formato(datos)

    ancho_dominio = max(len(tabla[0][0]), len(datos['dominio'])) + 4
    ancho_servidor = max(len(tabla[0][1]), max(len(s) for s in datos['solo_dominios'] + [""])) + 4
    ancho_ipv4 = max(len(tabla[0][2]), max(len(s) for s in datos['solo_ipv4'] + [""])) + 4
    ancho_asn = max(len(tabla[0][3]), max(len(s) for s in datos['solo_asn'] + [""])) + 4
    for fila in tabla:
        print("{: <{ancho_dominio}} {: <{ancho_servidor}} {: <{ancho_ipv4}} {: <{ancho_asn}}".format(*fila, ancho_dominio=ancho_dominio, ancho_servidor=ancho_servidor, ancho_ipv4=ancho_ipv4, ancho_asn=ancho_asn))

# TODO: otros formatos CSV de exportación
# TODO: más documentación de instalación, uso, ejemplos
# TODO: más documentación sobre el JSON generado
# TODO: más control de errores / excepciones
# TODO: lanzar sobre una lista de dominios
parser = argparse.ArgumentParser(description='Muestra los servidores que hacen autoridad sobre un dominio. Por defecto muestra los resultados en CSV, con tabulaciones para delimitar')
parser.add_argument('dominio', type=str, help='el nombre de dominio a analizar')
group = parser.add_mutually_exclusive_group()
group.add_argument('-j', '--json', action='store_true', help='formato de salida en JSON')
group.add_argument('-p', '--pretty-print', action='store_true', help='formato de salida elegante')
group.add_argument('-s', '--stats', action='store_true', help='mostrar solo estadísticas')
group.add_argument('-d', '--solo-dominios', action='store_true', help='solo mostrar los nombres de dominios de los servidores (puede incluir duplicados)')
group.add_argument('-i', '--solo-ipv4', action='store_true', help='solo mostrar las direcciones IPv4 de los servidores (puede incluir duplicados)')
group.add_argument('-a', '--solo-asn', action='store_true', help='solo mostrar los ASN de las direcciones IPv4 de los servidores (puede incluir duplicados)')
args = parser.parse_args()

solo_dominios = args.solo_dominios
solo_ipv4 = args.solo_ipv4
solo_asn = args.solo_asn
stats = args.stats
pretty_print = args.pretty_print
formato_json = args.json

# TODO: verificar si dominio es un dominio correcto, y si esta debajo de .gob.bo
dominio = dns.name.from_text(args.dominio).to_text()

datos = buscar_servidores_autoridad(dominio)

if solo_dominios:
    for d in datos['solo_dominios']:
        print(d)
elif solo_ipv4:
    for i in datos['solo_ipv4']:
        print(i)
elif solo_asn:
    for a in datos['solo_asn']:
        print(a)
elif formato_json:
    print(json.dumps(datos))
elif stats:
    formatear_stats(datos)
elif pretty_print:
    formatear_pretty_print(datos)
else:
    formatear_csv(datos)
