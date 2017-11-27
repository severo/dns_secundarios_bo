# DNS secundarios en Bolivia

Requisitos:

- https://github.com/hadiasghari/pyasn
- https://github.com/rthalley/dnspython

Instalación:

```
sudo pip install dnspython
sudo pip install pyasn --pre
pyasn_util_download.py --latest
pyasn_util_convert.py --single rib.* rib.txt
```
