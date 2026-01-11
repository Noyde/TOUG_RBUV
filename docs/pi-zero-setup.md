# Installation Raspberry Pi Zero 2 W

Guide d'installation pour la lecture Modbus de la PAC Aldes T.One RBUV via Pi Zero 2 W.

> ⚠️ **Limitation** : Cette méthode permet uniquement la **lecture** des registres. L'écriture n'est pas possible via USB.

---

## 1. Architecture
```
┌─────────────────────────────────────────────────────────────────────┐
│                         PAC ALDES T.One AIR                         │
│                                                                     │
│   ┌─────────────────┐                                               │
│   │ Port USB        │                                               │
│   │ (Mini-USB)      │                                               │
│   │ Bus Modbus      │                                               │
│   │ 1200 bauds      │                                               │
│   └────────┬────────┘                                               │
└────────────┼────────────────────────────────────────────────────────┘
             │ Câble USB (données + alimentation)
             │
┌────────────┴────────────┐
│   Raspberry Pi Zero 2 W │
│                         │
│   ┌─────────────────┐   │
│   │ Adaptateur OTG  │   │
│   │ USB-A → Micro   │   │
│   └─────────────────┘   │
│                         │
│   Script Python         │
│   pac_aldes_mqtt.py     │
│   └── Modbus RTU        │
│   └── Publication MQTT  │
│                         │
│   WiFi → Réseau local   │
└─────────────────────────┘
             │
             │ MQTT
             ▼
┌─────────────────────────┐
│   Home Assistant        │
│                         │
│   - MQTT Discovery      │
│   - 41 entités          │
│   - Dashboard PAC       │
└─────────────────────────┘
```

---

## 2. Matériel nécessaire

| Composant | Référence | Prix approx. |
|-----------|-----------|--------------|
| Raspberry Pi Zero 2 W | Pi Zero 2 W | ~18€ |
| Carte microSD | 16 Go minimum | ~5€ |
| Adaptateur USB OTG | USB-A → Micro-USB | ~3€ |
| Câble USB | USB-A → Mini-USB | ~2€ |
| **Total** | | **~28€** |

---

## 3. Installation du système

### 3.1 Préparation de la carte SD

1. Télécharger [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Sélectionner : **Raspberry Pi OS Lite (64-bit)**
3. Cliquer sur l'engrenage ⚙️ pour configurer :

| Paramètre | Valeur |
|-----------|--------|
| Hostname | `pac-reader` |
| SSH | ✅ Activé (mot de passe) |
| Utilisateur | (votre choix) |
| Mot de passe | (votre choix) |
| WiFi SSID | (votre réseau) |
| WiFi Password | (votre mot de passe) |
| Pays WiFi | FR |
| Fuseau horaire | Europe/Paris |

4. Flasher la carte SD

### 3.2 Premier démarrage

1. Insérer la carte SD dans le Pi Zero
2. Brancher l'adaptateur OTG sur le port **USB** (milieu, pas PWR)
3. Connecter à la PAC via câble USB
4. Attendre 2-3 minutes le démarrage
5. Se connecter en SSH :
```bash
   ssh utilisateur@pac-reader.local
```

### 3.3 Installation des dépendances
```bash
sudo apt update && sudo apt install -y python3-pip python3-serial
pip3 install paho-mqtt pyserial --break-system-packages
```

### 3.4 Ajouter l'utilisateur au groupe dialout
```bash
sudo usermod -a -G dialout $USER
exit  # Se déconnecter et reconnecter
```

### 3.5 Vérifier le port USB
```bash
ls -la /dev/ttyACM*
```

Résultat attendu : `/dev/ttyACM1`

---

## 4. Configuration Modbus

### 4.1 Paramètres de communication

| Paramètre | Valeur |
|-----------|--------|
| **Port série** | `/dev/ttyACM1` |
| **Baudrate** | 1200 |
| **Parité** | EVEN |
| **Stop bits** | 1 |
| **Adresse Modbus** | 0x01 |
| **Intervalle lecture** | 30 secondes |

### 4.2 Modes PAC

| Code | Mode |
|------|------|
| 2 | Rafraîchissement |
| 4 | Chauffage |
| 5 | Off |

---

## 5. Installation du script

### 5.1 Télécharger le script et la config
```bash
# Télécharger le script et le fichier config exemple
wget https://raw.githubusercontent.com/Noyde/TOUG_RBUV/main/tools/pac_aldes_mqtt.py
wget https://raw.githubusercontent.com/Noyde/TOUG_RBUV/main/tools/config_example.json

# Créer votre fichier de configuration
cp config_example.json config.json

# Éditer la configuration
nano config.json
```

### 5.2 Configurer config.json
```json
{
  "mqtt": {
    "broker": "192.168.x.x",
    "port": 1883,
    "user": "votre_user",
    "password": "votre_password"
  },
  "serial": {
    "port": "/dev/ttyACM1",
    "baudrate": 1200
  },
  "read_interval": 30,
  "zones": {
    "zone1": "Salon",
    "zone2": "Chambre 1",
    "zone3": "Chambre 2",
    "zone4": "Chambre 3",
    "zone5": "Chambre 4"
  }
}
```

### 5.3 Explication des paramètres

| Section | Paramètre | Description |
|---------|-----------|-------------|
| **mqtt** | `broker` | Adresse IP de votre serveur MQTT (Home Assistant) |
| | `port` | Port MQTT (1883 par défaut) |
| | `user` | Utilisateur MQTT |
| | `password` | Mot de passe MQTT |
| **serial** | `port` | Port série USB (`/dev/ttyACM1` généralement) |
| | `baudrate` | Vitesse communication (toujours `1200` pour RBUV) |
| **read_interval** | | Intervalle de lecture en secondes (30 recommandé) |
| **zones** | `zone1` | Nom Zone 1 (R20/R21 - même thermostat) |
| | `zone2` | Nom Zone 2 (R22) |
| | `zone3` | Nom Zone 3 (R23) |
| | `zone4` | Nom Zone 4 (R24) |
| | `zone5` | Nom Zone 5 (R25) |

> **Note** : Les noms de zones apparaîtront dans Home Assistant (ex: "Température Salon", "Consigne Chambre 1").
>
> **Important** : Le mapping RBUV utilise 5 zones : R20/R21 = même thermostat (Zone 1), R22-R25 = Zones 2-5.

---

## 6. Service systemd

### 6.1 Créer le fichier service
```bash
sudo nano /etc/systemd/system/pac_aldes.service
```

Contenu :
```ini
[Unit]
Description=PAC Aldes T.One MQTT Reader
After=network.target

[Service]
Type=simple
User=VOTRE_UTILISATEUR
Group=VOTRE_UTILISATEUR
WorkingDirectory=/home/VOTRE_UTILISATEUR
ExecStart=/usr/bin/python3 /home/VOTRE_UTILISATEUR/pac_aldes_mqtt.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 6.2 Activer le service
```bash
sudo systemctl daemon-reload
sudo systemctl enable pac_aldes
sudo systemctl start pac_aldes
```

### 6.3 Commandes utiles
```bash
# Vérifier le statut
sudo systemctl status pac_aldes

# Voir les logs en temps réel
sudo journalctl -u pac_aldes -f

# Redémarrer le service
sudo systemctl restart pac_aldes

# Arrêter le service
sudo systemctl stop pac_aldes
```

---

## 7. Intégration Home Assistant

### 7.1 MQTT Discovery

Le script publie automatiquement la configuration MQTT Discovery. Les entités apparaissent dans :

**Paramètres → Appareils et services → MQTT → PAC Aldes T.One AIR**

### 7.2 Entités créées (41 total)

| Catégorie | Nombre |
|-----------|--------|
| Températures pièces | 6 |
| Consignes | 6 |
| Températures PAC | 5 |
| Compresseur | 6 |
| Ventilation | 4 |
| EEV | 2 |
| Débits/Pressions | 5 |
| Système | 6 |
| Mode PAC (Texte) | 1 |

> **Note** : R16/R17 (Date/Heure) non inclus - non fonctionnels sur RBUV via USB.

---

## 8. Dépannage

### 8.1 Problèmes courants

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| Pi ne démarre pas sur USB PAC | Courant insuffisant | Alimentation externe via port PWR |
| Port série non détecté | Câble ou adaptateur défectueux | Vérifier `/dev/ttyACM1` |
| Erreur connexion MQTT | Mauvaise IP broker | Vérifier MQTT_BROKER dans le script |
| Valeurs aberrantes | Mauvais diviseur | Vérifier le script |
| Service ne démarre pas | Mauvais chemin/utilisateur | Vérifier pac_aldes.service |

### 8.2 Commandes de diagnostic
```bash
# Vérifier le port série
ls -la /dev/ttyACM* /dev/ttyUSB*

# Tester la connexion série
python3 -c "import serial; s=serial.Serial('/dev/ttyACM1', 1200); print('OK')"

# Vérifier la connectivité réseau
ping -c 3 <IP_BROKER_MQTT>

# Logs en temps réel
sudo journalctl -u pac_aldes -f

# Test manuel du script
python3 ~/pac_aldes_mqtt.py
```

### 8.3 Rollback

En cas de problème :
1. Débrancher le Pi de la PAC
2. La PAC fonctionne normalement sans le Pi
3. Les thermostats restent opérationnels

---

## 9. Ressources

| Ressource | Lien |
|-----------|------|
| Projet TOUG (djtef) | https://github.com/djtef/toug |
| Forum HACF | https://forum.hacf.fr/t/aldes-t-one-air-aquaair/42974 |
| Doc Aldes officielle | https://assets.aldes.fr/assets/docsFR/t.one-air-notice-d-installation-d-entretien-de-maintenance.pdf |

---

*Guide d'installation Pi Zero 2 W pour TOUG_RBUV*
