# Configuration ESPHome pour TOUG_RBUV

Configuration ESPHome pour les PAC Aldes T.One RBUV (modèles 2018 et antérieurs).

---

## Structure des fichiers
```
esphome/
├── aldes-tone-rbuv.yaml          # Configuration principale
├── secrets_example.yaml          # Exemple de configuration secrets
├── secrets.yaml                  # Vos secrets (gitignore)
├── components/
│   └── aldes_tone/
│       ├── __init__.py           # Définition composant Python
│       └── aldes_tone.h          # Code C++ protocole 0x17
└── README.md                     # Ce fichier
```

---

## Installation

### 1. Copier les fichiers

Copiez le contenu de ce dossier dans votre configuration ESPHome :
```
/config/esphome/
├── aldes-tone-rbuv.yaml
└── components/
    └── aldes_tone/
        ├── __init__.py
        └── aldes_tone.h
```

### 2. Configurer secrets.yaml

Copiez l'exemple et configurez vos valeurs :
```bash
cp secrets_example.yaml secrets.yaml
nano secrets.yaml
```

Contenu de `secrets.yaml` :
```yaml
# WiFi
wifi_ssid: "VotreSSID"
wifi_password: "VotreMotDePasse"

# API ESPHome (optionnel)
api_encryption_key: ""

# OTA (optionnel)
ota_password: ""

# Noms des zones (personnalisables)
zone1_name: "Zone 1"
zone1bis_name: "Zone 1 bis"
zone2_name: "Zone 2"
zone3_name: "Zone 3"
zone4_name: "Zone 4"
zone5_name: "Zone 5"

# Noms des bouches (personnalisables)
bouche1a_name: "Bouche Zone 1a"
bouche1b_name: "Bouche Zone 1b"
bouche2_name: "Bouche Zone 2"
bouche3_name: "Bouche Zone 3"
bouche4_name: "Bouche Zone 4"
bouche5_name: "Bouche Zone 5"
```

### Explication des paramètres

| Paramètre | Description |
|-----------|-------------|
| `wifi_ssid` | Nom de votre réseau WiFi |
| `wifi_password` | Mot de passe WiFi |
| `api_encryption_key` | Clé chiffrement API ESPHome (laisser vide pour désactiver) |
| `ota_password` | Mot de passe pour mises à jour OTA (laisser vide pour désactiver) |
| `zone1_name` | Nom Zone 1 (R20/R21 - même thermostat) |
| `zone1bis_name` | Nom Zone 1 bis (même thermostat que Zone 1) |
| `zone2_name` | Nom Zone 2 (R22) |
| `zone3_name` | Nom Zone 3 (R23) |
| `zone4_name` | Nom Zone 4 (R24) |
| `zone5_name` | Nom Zone 5 (R25) |
| `bouche1a_name` | Nom Bouche Zone 1a (GPIO34) |
| `bouche1b_name` | Nom Bouche Zone 1b (GPIO35) |
| `bouche2_name` | Nom Bouche Zone 2 (GPIO36) |
| `bouche3_name` | Nom Bouche Zone 3 (GPIO39) |
| `bouche4_name` | Nom Bouche Zone 4 (GPIO32) |
| `bouche5_name` | Nom Bouche Zone 5 (GPIO33) |

> **Note** : Le mapping RBUV utilise 5 thermostats : R20/R21 = même thermostat (Zone 1), R22-R25 = Zones 2-5.

### 3. Personnaliser les zones (optionnel)

Les noms de zones sont définis dans la section `substitutions` du YAML.
Vous pouvez les modifier directement ou les surcharger à la compilation :
```bash
esphome -s zone1_name "Mon Salon" run aldes-tone-rbuv.yaml
```

### 4. Compiler et flasher
```bash
esphome run aldes-tone-rbuv.yaml
```

---

## Prérequis matériel

| Composant | Description |
|-----------|-------------|
| ESP32 D1 Mini | WROOM-32 |
| Module RS485 | MAX485 |
| Level Shifter | BSS138 4ch |
| Step-Down | Mini360 (12V→5V) |

Voir [docs/hardware.md](../docs/hardware.md) pour les schémas de câblage.

---

## Important

**La télécommande Aldes doit être DÉBRANCHÉE** pour éviter les collisions sur le bus RS485.

---

## Modes disponibles

| Mode | Description |
|------|-------------|
| Off | Arrêt PAC |
| Chauffage Confort | Chauffage mode confort |
| Chauffage Eco | Chauffage mode économique |
| Clim Confort | Climatisation mode confort |
| Clim Boost | Climatisation mode boost |
| Vacances | Mode vacances |

---

## Entités créées

### Contrôle
- `select.mode_pac` - Sélection du mode

### Températures zones (6)
- `sensor.temperature_zone_1` à `sensor.temperature_zone_6`

### Consignes zones (6)
- `sensor.consigne_zone_1` à `sensor.consigne_zone_6`

### Températures PAC
- `sensor.temperature_exterieure`
- `sensor.temperature_air_repris`
- `sensor.temperature_echangeur_ui`
- `sensor.temperature_echangeur_ue`
- `sensor.temperature_sortie_compresseur`

### Compresseur / Ventilation
- `sensor.frequence_compresseur`
- `sensor.heures_compresseur`
- `sensor.vitesse_ventilateur`

### Vannes / Débits
- `sensor.eev1`, `sensor.eev2`
- `sensor.debit_nominal`
- `sensor.pression_statique`

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Erreurs CRC massives | Débrancher la télécommande Aldes |
| Écriture ne fonctionne pas | Vérifier câblage RS485 (A/B) |
| Compilation échoue | Vérifier structure dossiers components/ |

---

## Ressources

- [Projet TOUG (djtef)](https://github.com/djtef/toug)
- [Documentation ESPHome](https://esphome.io/)
- [Protocol 0x17](../docs/protocol.md)
