# Arkteos Proxy — Home Assistant Addon

Proxy TCP pour PAC Arkteos REG3 (Zuran 4, Baguio 4, etc.).

Permet les connexions simultanées de Node-RED et de l'application mobile Arkteos, en relayant le flux binaire de la PAC vers tous les clients connectés.

## Installation

1. Dans Home Assistant : **Paramètres → Modules complémentaires → Dépôts**
2. Ajoute l'URL de ce repo : `https://github.com/raph666/arkteos-proxy-addon`
3. Installe l'addon **Arkteos Proxy**
4. Configure l'IP de ta PAC dans les options
5. Démarre l'addon

## Configuration

| Option | Description | Défaut |
|---|---|---|
| `pac_host` | Adresse IP de la PAC | `192.168.0.10` |
| `pac_port` | Port TCP de la PAC | `9641` |
| `proxy_port` | Port d'écoute du proxy | `9641` |

## Utilisation avec Node-RED

Dans le nœud `tcp in` de Node-RED, connecte-toi à `IP_HA:<proxy_port>` au lieu de l'IP directe de la PAC.

## Protocole

La PAC Arkteos REG3 expose un flux binaire TCP (serial-over-IP) sur le port 9641 (IHM).
Trois types de trames sont émises en continu :
- 163 bytes : données groupe frigorifique
- 227 bytes : données régulation
- 95 bytes : métadonnées réseau

Toutes les trames commencent par le magic bytes `0x55 0x00`.
