# DNS secundarios en Bolivia

Requisitos:

- https://github.com/hadiasghari/pyasn
- https://github.com/rthalley/dnspython

Instalación:

```
sudo apt install parallel
sudo pip install dnspython
sudo pip install pyasn --pre
pyasn_util_download.py --latest
pyasn_util_convert.py --single rib.* rib.txt
```

Lanzar sobre un archivo de dominios, y guardar el resultado en un CSV:

```
$ parallel -a dominios.txt python secundarios.py -s > resultados.txt

agetic.gob.bo.	1	1	1
adsib.gob.bo.	0	0	0
aduana.gob.bo.	3	3	2
rednegra.net.	5	5	3
```
