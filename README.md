# Arkteos Proxy — Home Assistant Addon

Proxy TCP pour PAC Arkteos REG3 (Zuran 4, Baguio 4, etc.).

Permet les connexions simultanées de Node-RED et de l'application mobile Arkteos, en relayant le flux binaire de la PAC vers tous les clients connectés.

## Installation

1. Dans Home Assistant : **Paramètres → Modules complémentaires → trois points → Dépôts**
2. Ajoute l'URL de ce repo : `https://github.com/raph666/arkteos-proxy-addon`
3. Installe l'addon **Arkteos Proxy**
4. Configure l'IP de ta PAC dans les options
5. Configure le port exposé dans la section **Network** (défaut : 9641) et clique **Save**
6. Démarre l'addon

## Configuration

| Option | Description | Défaut |
|---|---|---|
| `pac_host` | Adresse IP de la PAC | `192.168.X.X` |
| `pac_port` | Port TCP de la PAC | `9641` |
| `proxy_port` | Port d'écoute interne du proxy | `9641` |

## Intégration Node-RED

Un flow Node-RED prêt à l'emploi est disponible dans ce repo : `nodered/arkteos_reg3_nodered.json`.

### Import

1. Dans Node-RED : menu hamburger → **Import** → colle le contenu du fichier JSON
2. Double-clique sur le nœud **PAC via proxy** et remplace `<IP_HA>` par l'IP de ton Home Assistant
3. Double-clique sur le nœud **MQTT publish** → icône crayon → onglet **Security** → renseigne le login et mot de passe Mosquitto
4. Clique **Deploy**

### Fonctionnement

Le flow se connecte en streaming permanent au proxy. Chaque trame reçue est parsée et les valeurs sont publiées sur MQTT avec un système de throttling :

- une valeur n'est publiée que si elle a changé au-delà d'un seuil défini
- une publication forcée a lieu toutes les 30 ou 60 secondes même sans changement

| Valeur | Seuil | Intervalle max |
|---|---|---|
| Températures | 0.5°C | 60s |
| Puissances | 0.1 kW | 30s |
| Pression | 0.1 bar | 60s |
| Fréquence compresseur | 1 Hz | 30s |
| Voltage DC | 5 V | 60s |

### Entités créées dans HA

Le flow publie automatiquement 12 entités via MQTT Discovery dans un appareil **PAC Arkteos Zuran 4** :

**Groupe frigorifique**
- Température extérieure (°C)
- Fréquence compresseur actuelle (Hz)
- Voltage DC compresseur (V)

**Régulation**
- Puissance instantanée produite (kW)
- Puissance instantanée consommée (kW)
- Température eau primaire aller (°C)
- Température eau primaire retour (°C)
- Pression eau primaire (bar)
- Température intérieure zone 1 (°C)
- Consigne température zone 1 (°C)
- Température ballon ECS milieu (°C)
- Température ballon ECS bas (°C)

## Protocole

La PAC Arkteos REG3 expose un flux binaire TCP (serial-over-IP) sur le port 9641 (IHM).
Trois types de trames sont émises en continu à environ 1 trame/seconde :

| Taille | Type | Contenu |
|---|---|---|
| 163 bytes | Frigo | Données groupe frigorifique Mitsubishi |
| 227 bytes | Régulation | Données régulation, températures, ECS |
| 95 bytes | Réseau | Métadonnées de connexion (IP PAC, etc.) |

Toutes les trames commencent par le magic bytes `0x55 0x00`.
