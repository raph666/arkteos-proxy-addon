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

Le flow se connecte en streaming permanent au proxy. Chaque trame reçue est parsée, filtrée puis publiée sur MQTT.

**Filtrage des valeurs aberrantes**

Les valeurs hors plage physiquement plausible sont ignorées et loguées dans la console Node-RED :

| Valeur | Plage valide |
|---|---|
| Température extérieure | -50°C à 150°C |
| Températures circuit primaire | -10°C à 90°C |
| Consigne départ eau primaire | -10°C à 90°C |
| Températures ECS | 0°C à 95°C |
| Consigne ECS | 0°C à 80°C |
| Température intérieure zone 1 | -10°C à 50°C |
| Consigne zone 1 | 5°C à 35°C |
| Puissances | 0 à 50 000 W |
| Pression eau primaire | 0 à 10 bar |
| Fréquence compresseur actuelle | 0 à 200 Hz |
| Fréquence compresseur cible | 0 à 200 Hz |
| Vitesse ventilateur | 0 à 3 000 rpm |
| Voltage DC | 0 à 1 000 V |
| Débit eau primaire | 0 à 10 000 L/h |
| Circulateur primaire | 0% à 100% |
| Statut frigo | 0 à 3 |
| Statut PAC | 0 à 9 |
| Signal RF sonde | -128 à 127 dBm |
| Nb cycles compresseur | 0 à 9 999 999 |
| Temps fonctionnement compresseur | 0 à 999 999 h |
| Temps mise sous tension | 0 à 999 999 h |

**Throttling**

Une valeur n'est publiée que si elle a changé au-delà d'un seuil défini, avec un rafraîchissement forcé à intervalle maximum :

| Valeur | Seuil | Intervalle max |
|---|---|---|
| Température extérieure | 0.5°C | 60s |
| Températures circuit primaire | 0.5°C | 60s |
| Consigne départ eau primaire | 0.5°C | 60s |
| Températures ECS | 0.5°C | 60s |
| Consigne ECS | 0.5°C | 60s |
| Température intérieure zone 1 | 0.5°C | 60s |
| Consigne zone 1 | 0.5°C | 60s |
| Puissance produite | 10 W | 30s |
| Puissance consommée | 10 W | 30s |
| Pression eau primaire | 0.1 bar | 60s |
| Fréquence compresseur actuelle | 1 Hz | 30s |
| Fréquence compresseur cible | 1 Hz | 30s |
| Vitesse ventilateur | 10 rpm | 30s |
| Voltage DC | 5 V | 60s |
| Débit eau primaire | 1 L/h | 60s |
| Circulateur primaire | 1% | 60s |
| Modèle PAC | changement | 1h |
| Statut frigo | changement | 60s |
| Statut PAC | changement | 60s |
| Erreurs | changement | 60s |
| Nb cycles compresseur | 100 | 5 min |
| Temps fonctionnement compresseur | 1 h | 5 min |
| Temps mise sous tension | 1 h | 5 min |
| Signal RF sonde | 1 dBm | 5 min |

**Statut de connexion**

Un `binary_sensor` HA indique si la PAC est connectée. Il passe à `OFF` si aucune trame n'est reçue depuis plus de 30 secondes.

### Entités créées dans HA

Le flow publie automatiquement via MQTT Discovery dans un appareil **PAC Arkteos Zuran 4** :

**Statut**
- PAC connectée (binary_sensor)

**Groupe frigorifique**
- Température extérieure (°C)
- Nombre de dégivrages
- Temps fonctionnement compresseur (h)
- Nombre de cycles compresseur
- Fréquence compresseur actuelle (Hz)
- Fréquence compresseur cible (Hz)
- Vitesse ventilateur groupe frigo (rpm)
- Voltage DC compresseur (V)
- Statut frigo (0-3)
- Statut frigo texte (Arret / Refroidissement / Chauffage / Degivrage)
- Erreur active frigo

**Régulation**
- Puissance instantanée produite (W)
- Puissance instantanée consommée (W)
- Temps mise sous tension (h)
- Modèle PAC (texte)
- Consigne départ eau primaire (°C)
- Température eau primaire aller (°C)
- Température eau primaire retour (°C)
- Débit eau primaire (L/h)
- Pression eau primaire (bar)
- Circulateur primaire (%)
- Température intérieure zone 1 (°C)
- Consigne température zone 1 (°C)
- Température ballon ECS milieu (°C)
- Température ballon ECS bas (°C)
- Consigne ECS (°C)
- Cycles compresseur (régulation)
- Statut PAC (0-9)
- Statut PAC texte (Arret / Attente / Chaud / Froid / Hors Gel / ECS / Piscine / etc.)
- Erreur active régulation
- Signal RF sonde zone 1 (dBm)

## Protocole

La PAC Arkteos REG3 expose un flux binaire TCP (serial-over-IP) sur le port 9641 (IHM).
Trois types de trames sont émises en continu à environ 1 trame/seconde :

| Taille | Type | Contenu |
|---|---|---|
| 163 bytes | Frigo | Données groupe frigorifique Mitsubishi |
| 227 bytes | Régulation | Données régulation, températures, ECS |
| 95 bytes | Réseau | Métadonnées de connexion (IP PAC, etc.) |

Toutes les trames commencent par le magic bytes `0x55 0x00`.
