#!/usr/bin/python
# -*- coding: UTF-8 -*-

import argparse
import dns.name
import dns.resolver
import pyasn
import json

# Initialize module and load IP to ASN database
# the sample database can be downloaded or built - see below
asndb = pyasn.pyasn('rib.20171126.2200.txt')

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
    respuesta = {'dominio': dominio, 'servidores_NS': []}

    # Consulta clave "NS"
    lista_NS = buscar_lista_NS(respuesta['dominio'])
    for NS in lista_NS:
        servidor_NS = {'dominio': NS, 'direcciones_ipv4': []}
        lista_ipv4 = buscar_lista_ipv4(NS)
        for ipv4 in lista_ipv4:
            asn = buscar_asn_ipv4(ipv4)
            servidor_NS['direcciones_ipv4'].append({'ipv4': ipv4, 'asn': asn})
        respuesta['servidores_NS'].append(servidor_NS)
    return json.dumps(respuesta)

parser = argparse.ArgumentParser(description='Muestra los servidores que hacen autoridad sobre un dominio.')
parser.add_argument('dominio', type=str, help='el nombre de dominio a analizar')
args = parser.parse_args()

# TODO: verificar si dominio es un dominio correcto, y si esta debajo de .gob.bo
dominio = dns.name.from_text(args.dominio).to_text()

print(buscar_servidores_autoridad(dominio))
