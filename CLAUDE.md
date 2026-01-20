# Contexte projet TOUG_RBUV

## Résumé

Domotisation PAC Aldes T.One AIR RBUV (2018) via Home Assistant. Modèle : T.One AIR 04 (RBC04MX/RBUV04F), firmware 3019.

C'est un complément au projet [TOUG](https://github.com/djtef/toug) de @djtef, adapté aux spécificités des anciens modèles.

## Découvertes clés

### Protocole propriétaire 0x17
- Fonctions Modbus standard (0x06, 0x10) → `illegal data address` ou `illegal function`
- Seule la fonction 0x17 (Read/Write Multiple) fonctionne pour l'écriture
- Trames de 74 bytes comme la télécommande Aldes

### Deux bus
| Bus | Baudrate | Lecture | Écriture |
|-----|----------|---------|----------|
| USB | 1200 | ✅ | ❌ |
| RS485 télécommande | 19200 | ✅ | ✅ (0x17) |

### Limitations hardware confirmées
- Consignes thermostats (R20-R25) = read-only (pilotées par radio 868MHz)
- Registres TOUG 31100-31104 = non implémentés sur **aucun modèle** (confirmé par @djtef)

### État des bouches via réponse 0x17 - VALIDÉ 2025-01-15
- R5029 (bitmap TOUG) → retourne 0 sur RBUV via USB et RS485
- **Découverte** : Byte 33 de la réponse `01 17 80 0b` = bitmap des bouches actives !
- K1a=0x01, K1b=0x02, K3=0x04, K4=0x08, K5=0x10, K6=0x20
- R77 via USB donne uniquement l'index de la dernière zone (pas un bitmap)
- **Pas besoin d'optocouplers** pour lire l'état des bouches sur RBUV

### IDs thermostats 868MHz dans réponse 0x17 - CONFIRMÉ 2025-01-20
- Offsets 89-112 de la réponse `01 17 80 0b` contiennent les 6 IDs thermostats
- Format : 4 bytes par ID, encodage **little-endian**
- Exemple : `e7 87 00 f3` → ID 00F3E787
- TH1 et TH2 partagent le même ID (K1a et K1b sur même thermostat physique)

### Consignes zones dans réponse 0x17 - VALIDÉ 2025-01-20
- Offsets 42-53 de la réponse `01 17 80 0b` = consignes thermostats (6×2 bytes)
- Équivalent aux registres R20-R25 via USB
- Format : big-endian, ÷100 pour °C
- Validation : Correspondance parfaite sur capture synchronisée

### Températures zones dans réponse 0x17 - VALIDÉ 2025-01-20
- Offsets 74-85 de la réponse `01 17 80 0b` = températures mesurées (6×2 bytes)
- Équivalent aux registres R36-R41 via USB
- Format : big-endian, ÷100 pour °C
- Validation : Correspondance parfaite sur capture synchronisée

### Régulation zones INDÉPENDANTE du protocole 0x17
- Les thermostats 868MHz communiquent **directement** avec le régulateur PAC
- Les bouches motorisées s'ouvrent/ferment **sans avoir besoin** de trames 0x17
- Le protocole 0x17 sert **uniquement** à changer le MODE (On/Off, Chauffage/Clim, Eco/Boost, Vacances)
- **Validé 2025-01-13** : Test sans télécommande ni trames 0x17 → bouches réagissent aux thermostats

### Trame `21 xx` - Communication interne PAC - DÉCOUVERTE 2025-01-20
- Trame différente de `01 17`, communication interne PAC
- **Courant compresseur** à offset 84-85 (÷100 pour Ampères) - **SEULE SOURCE !**
- Heures ventilateur à offset 90-91, Heures compresseur à offset 94-95
- Températures internes (air repris, échangeurs) aux offsets 62-69
- Niveau ventil UE à offset 56
- ⚠️ T° sortie compresseur (~70°C) à localiser dans cette trame

### Mapping registres différent (RBUV sans ECS)
| Registre | TOUG (avec ECS) | RBUV (sans ECS) |
|----------|-----------------|-----------------|
| R39 | T° extérieure | T° Zone 4 |
| R112 | Sonde ECS bas | **T° extérieure** |
| R117 | Échangeur capillaire | **T° sortie compresseur** |
| R44 | T° sortie compresseur | ❌ Non implémenté |

## Structure trame 0x17 (74 bytes) - VALIDÉ 2025-01-13

| Offset | Description | Valeurs |
|--------|-------------|---------|
| 0-1 | Adresse + Fonction | 0x01, 0x17 |
| 2-3 | Sous-code séquence | Cycle: 0x0001→0x0041→0x0081→0x00C1 |
| 10-11 | Signature | 0x7370 ("sp") |
| 14-15 | Compteur | Incrémente à chaque trame |
| **18-19** | **Niveau** | 0x0000=Confort, 0x00C8=Eco |
| **20-21** | **Boost** | 0x0000=Normal, 0x5678=Boost |
| **24-25** | **Flag service** | 0x0000=Normal, 0x3412=Mode installateur |
| **26-27** | **Débit nominal** | m³/h (ex: 0x0384=900) |
| **28-29** | **PSE nominal** | Pa (ex: 0x0017=23) |
| **30-31** | **Débit 1 bouche** | m³/h (ex: 0x00F0=240) |
| **32-33** | **PSE mini** | Pa (ex: 0x000C=12) |
| **34-35** | **Vacances** | 0x0000=Off, 0x1234=On |
| **36-37** | **On/Off** | 0x0002=Off, 0x0003=On |
| **38-39** | **Type mode** | 0x000A=Clim, 0x000B=Service, 0x000C=Chauffage |
| 40-69 | Consignes zones | Pattern 0x7FFE = pas de changement |
| 72-73 | CRC16 Modbus | Calculé sur bytes 0-71 |

> ⚠️ **Note** : La date/heure n'est PAS transmise dans la trame 0x17 (validé X19-X20)

## Mapping thermostats corrigé
| Registre | Zone |
|----------|------|
| 20 | Zone 1 (K1a) |
| 21 | Zone 1 bis (K1b) - même thermostat que 20 |
| 22 | Zone 2 |
| 23 | Zone 3 |
| 24 | Zone 4 |
| 25 | Zone 5 |

## Statut projet
- ✅ Lecture 40 registres via Pi Zero USB (auto-détection port série)
- ✅ Protocole 0x17 documenté et **validé par sniffing** (2025-01-13)
- ✅ Tests sniffing X01-X20 complétés (modes, ventilation, date/heure)
- ✅ Tests envoi Y01-Y07 validés via Pi 2B RS485 (2025-01-13)
- ✅ Composant ESPHome mis à jour avec offsets corrigés (2025-01-13)
- ✅ **État bouches découvert** : byte 33 réponse 0x17 = bitmap (2025-01-15)
- ✅ **Trame `21 xx` découverte** : courant compresseur, heures, T° internes (2025-01-20)
- ⚠️ T° sortie compresseur à localiser dans trame `21 xx`
- ⚠️ Tests envoi ESP32 à faire (même protocole, validation finale)
- ⚠️ Projet BETA - utilisation à vos risques

## Ressources
- Repo: https://github.com/Noyde/TOUG_RBUV
- TOUG (djtef): https://github.com/djtef/toug
- Forum HACF: https://forum.hacf.fr/t/aldes-t-one-air-aquaair/42974

---

## Structure du dépôt

```
TOUG_RBUV/
├── README.md                    # Documentation principale (FR)
├── LICENSE                      # Licence MIT
├── .gitignore                   # Exclusions git
├── CLAUDE.md                    # Instructions pour Claude Code
├── docs/                        # Documentation technique
│   ├── hardware.md              # Schémas de câblage matériel
│   ├── pi-zero-setup.md         # Guide installation Raspberry Pi
│   ├── protocol.md              # Documentation protocole 0x17
│   └── registers.md             # Mapping des 40 registres Modbus
├── esphome/                     # Configuration ESPHome
│   ├── README.md                # Guide ESPHome
│   ├── aldes-tone-rbuv.yaml     # Configuration principale YAML
│   ├── secrets_example.yaml     # Exemple secrets (copier en secrets.yaml)
│   └── components/              # Composant custom ESPHome
│       └── aldes_tone/
│           ├── __init__.py      # Définition composant Python
│           └── aldes_tone.h     # Code C++ protocole 0x17
├── tests/                       # Tests et validation
│   ├── README.md                # Matrice de tests TOUG + RBUV
│   └── results/                 # Résultats horodatés
└── tools/                       # Scripts et services
    ├── pac_aldes_mqtt.py         # Script Python Modbus→MQTT
    ├── config_example.json        # Config exemple (copier en config.json)
    └── pac_aldes.service          # Service systemd
```

---

## Matériel disponible pour tests

### Raspberry Pi 2B (sniffing RS485)
- Convertisseur USB-RS485 Waveshare (FT232RL)
- Port : /dev/ttyUSB0
- Utilisé pour capturer les trames télécommande ↔ PAC
- Connexion en parallèle sur le bus télécommande via Wago
- Paramètres : 19200 bauds, 8 bits, parité EVEN, 1 stop

### Raspberry Pi Zero 2 W (lecture USB)
- Connecté au port USB de la PAC
- Port : /dev/ttyACM1
- Script pac_aldes_mqtt.py actif (service systemd)
- Paramètres : 1200 bauds, parité EVEN

### ESP32 D1 Mini (écriture RS485)
- GPIO16 : UART RX (vers RS485 RO via level shifter)
- GPIO17 : UART TX (vers RS485 DI via level shifter)
- GPIO4 : Flow Control (DE + RE pontés)
- Alimentation via Step-Down Mini360 (~4.4V depuis 12V PAC)

---

## Tests à refaire et documenter

### Tests lecture Modbus ✅ COMPLÉTÉS (2025-01-10)

| Test | Bus | Baudrate | Registres | Statut |
|------|-----|----------|-----------|--------|
| Lecture R1-R9 (système) | USB | 1200 | 1,3,9 | ✅ OK |
| Lecture R20-R25 (consignes) | USB | 1200 | 20-25 | ✅ OK |
| Lecture R36-R41 (températures zones) | USB | 1200 | 36-41 | ✅ OK |
| Lecture R60-R66 (ventilation/compresseur) | USB | 1200 | 60-66 | ✅ OK |
| Lecture R104-R117 (PAC interne) | USB | 1200 | 104-117 | ✅ OK |
| Lecture R247-R251 (débits/pressions) | USB | 1200 | 247-251 | ✅ OK |
| Lecture via bus télécommande | RS485 | 19200 | Tous | ⬜ À faire |

### Tests écriture Modbus standard ✅ USB COMPLÉTÉS (2025-01-10)

| Test | Bus | FC | Registre | Résultat |
|------|-----|-----|----------|----------|
| Écriture R9 (mode) | USB | 0x06 | 9 | ✅ illegal function |
| Écriture R9 (mode) | USB | 0x10 | 9 | ✅ illegal data address |
| Écriture R9 (mode) | RS485 | 0x06 | 9 | ⬜ À faire |
| Écriture R9 (mode) | RS485 | 0x10 | 9 | ⬜ À faire |
| Écriture R20 (consigne) | USB | 0x06 | 20 | ✅ illegal data address |
| Écriture R31100-31104 (TOUG) | USB | 0x06 | 31100+ | ✅ illegal data address |

### Tests protocole 0x17 (sniffing télécommande) ✅ VALIDÉS 2025-01-13

| Test | Action | Offset | Valeur | Statut |
|------|--------|--------|--------|--------|
| X01-X02 | On/Off | 36-37 | 0x0002/0x0003 | ✅ |
| X03-X04 | Eco/Confort | 18-19 | 0x00C8/0x0000 | ✅ |
| X05-X06 | Chauffage/Clim | 38-39 | 0x000C/0x000A | ✅ |
| X07 | Boost | 20-21 | 0x5678 | ✅ |
| X08-X09 | Vacances | 34-35 | 0x1234/0x0000 | ✅ |
| X11-X12 | Débit nominal | 26-27 | m³/h | ✅ |
| X13-X14 | PSE nominal | 28-29 | Pa | ✅ |
| X15-X16 | Débit 1 bouche | 30-31 | m³/h | ✅ |
| X17-X18 | PSE mini | 32-33 | Pa | ✅ |
| X19-X20 | Date/heure | - | Non transmise | ❌ |

> **Découvertes clés** : Flag mode service (24-25=0x3412), Type mode étendu (38-39 inclut 0x000B=Service)

### Tests envoi trame 0x17 (Pi 2B RS485 → PAC) ✅ VALIDÉS 2025-01-13

| Test | Mode | Offset | Valeur | R9 | Statut |
|------|------|--------|--------|-----|--------|
| Y01 | Off | 36-37 | 0x0002 | 5 | ✅ |
| Y02 | Chauffage Confort | 36-37, 38-39 | 0x0003, 0x000C | 4 | ✅ |
| Y03 | Chauffage Eco | 18-19 | 0x00C8 | 4 | ✅ |
| Y04 | Clim Confort | 38-39 | 0x000A | 2 | ✅ |
| Y05 | Clim Boost | 20-21 | 0x5678 | 2 | ✅ |
| Y06 | Vacances On | 34-35 | 0x1234 | - | ✅ |
| Y07 | Retour normal | 34-35 | 0x0000 | 4 | ✅ |

> **Note** : Eco/Boost non distinguables via R9 (pas de registre Modbus dédié). Script: `tools/test_send_0x17.py`

### Commandes de test

```bash
# Lecture registre via Pi Zero (USB 1200 bauds)
python3 -c "
import minimalmodbus
instr = minimalmodbus.Instrument('/dev/ttyACM1', 1)
instr.serial.baudrate = 1200
instr.serial.parity = 'E'
instr.serial.timeout = 1
print(f'R9: {instr.read_register(9)}')
"

# Capture RS485 télécommande (Pi 2B)
stty -F /dev/ttyUSB0 19200 cs8 parenb -parodd -cstopb raw -echo
timeout 30 cat /dev/ttyUSB0 > /tmp/capture.bin
xxd /tmp/capture.bin | head -50
```

---

## Fichiers clés et leur rôle

### `esphome/aldes-tone-rbuv.yaml`
Configuration principale ESPHome. Définit :
- Les 40 capteurs Modbus (températures, consignes, fréquences, etc.)
- Le sélecteur de mode PAC (Off, Chauffage Confort/Eco, Clim Confort/Boost, Vacances)
- La configuration UART pour RS485 (GPIO16 RX, GPIO17 TX, GPIO4 flow control)
- Noms de zones personnalisables via substitutions

### `esphome/secrets_example.yaml`
Fichier de configuration exemple (copier en `secrets.yaml`) :
- Credentials WiFi (ssid, password)
- Clés API/OTA (optionnelles)

### `esphome/components/aldes_tone/aldes_tone.h`
Composant C++ ESPHome implémentant le protocole propriétaire 0x17 :
- Classe `AldesToneWriter` avec méthodes de contrôle (`set_off()`, `set_chauffage_confort()`, etc.)
- Fonction `send_frame()` pour construire et envoyer les trames 74 bytes
- Calcul CRC16 Modbus intégré

### `tools/pac_aldes_mqtt.py`
Script Python pour Raspberry Pi Zero. Configuration via `config.json` :
- Lecture des 40 registres via USB (lecture seule)
- **Auto-détection port série** : mettre `"port": "auto"` dans config.json
- Publication MQTT avec MQTT Discovery pour Home Assistant
- Noms de zones personnalisables via config.json

### `tools/config_example.json`
Fichier de configuration exemple (copier en `config.json`) :
- Credentials MQTT (broker, user, password)
- Port série : `"auto"` pour auto-détection ou chemin explicite (`/dev/ttyACM1`)
- Noms des 6 zones (personnalisables)

### `docs/protocol.md`
Documentation complète du protocole 0x17 :
- Structure des trames (74 bytes)
- Valeurs des champs de contrôle (niveau, vacances, on/off, type mode)
- Correspondance offset → registre Modbus

### `docs/registers.md`
Mapping des 40 registres Modbus :
- Registres système (R1, R3, R9, R14, R15, R51)
- Consignes thermostats (R20-R25) - **lecture seule hardware**
- Températures zones (R36-R41)
- Ventilation, compresseur, EEV, débits/pressions

---

## Conventions de développement

### Langue
- **Documentation** : Français
- **Code** : Anglais (noms de variables, fonctions)
- **Commentaires** : Français pour le contexte métier

### Style de code

#### Python (`tools/`)
- PEP 8
- Logging avec le module `logging`
- Configuration en constantes MAJUSCULES en haut du fichier

#### C++ (`esphome/components/`)
- Style ESPHome (basé sur Google C++ Style)
- Indentation 2 espaces
- Logs via `ESP_LOGI()`, `ESP_LOGW()`, `ESP_LOGE()`

#### YAML (`esphome/`)
- Indentation 2 espaces
- Commentaires de section avec `# ═══════════════`

### Commits

Messages préfixés :
- `Add:` - Nouvelle fonctionnalité
- `Fix:` - Correction de bug
- `Update:` - Mise à jour documentation/configuration
- `Refactor:` - Refactoring sans changement fonctionnel

---

## Valeurs importantes

### Modes PAC (Registre 9)

| Code | Mode |
|------|------|
| 2 | Rafraîchissement |
| 4 | Chauffage |
| 5 | Off |

### Registres avec diviseurs

| Type | Diviseur | Exemple |
|------|----------|---------|
| Températures | ÷100 | 2150 → 21.50°C |
| Fréquences | ÷10 | 450 → 45.0 Hz |
| Autres | ÷1 | Valeur brute |

---

## Limitations connues (NE PAS essayer de contourner)

1. **Consignes thermostats (R20-R25)** : READ-ONLY au niveau hardware. Pilotées par radio 868MHz.
2. **Télécommande Aldes** : Doit être DÉBRANCHÉE pour utiliser l'ESP32. Collisions garanties sinon.
3. **Écriture USB** : IMPOSSIBLE sur modèles 2018. Seul le bus RS485 accepte le protocole 0x17.
4. **Registres TOUG 31100-31104** : Ne fonctionnent sur **aucun modèle** T.One (confirmé par @djtef). Erreur dans la doc TOUG.
5. **Registres R16/R17 (Date/Heure)** : NON FONCTIONNELS sur RBUV via USB. Valeurs incohérentes lors de tests 2025-01-11.
6. **Date/heure via 0x17** : NON TRANSMISE dans la trame télécommande (validé X19-X20). Chaque appareil maintient sa propre horloge.

---

## Notes techniques

### Réponses protocole 0x17

La PAC répond aux trames 0x17 avec deux types de réponses :
- `0117 80xx` : Réponse principale contenant les données capteurs
- `0117 78xx` : Données additionnelles

Pas d'ACK explicite - la réponse contient directement les données.

### Cycle de la télécommande

La télécommande émet en continu avec un cycle de 4 sous-codes :
- 0x0001 → 0x0041 → 0x0081 → 0x00C1 → (répète)

**Une seule trame suffit à changer l'état de la PAC.** Pas de délai minimum identifié entre les envois.

### Méthode de découverte du protocole

Sniffing RS485 avec :
- Raspberry Pi 2B + convertisseur USB-RS485 Waveshare (FT232RL)
- Connexion en parallèle sur le bus télécommande via Wago

Les fonctions Modbus standard (0x03, 0x06, 0x10) retournaient `illegal data address` ou `illegal function`, ce qui a conduit à analyser les trames de la télécommande.

### Éléments validés (2025-01-10)

| Élément | Statut |
|---------|--------|
| Mapping registres TOUG vs RBUV | ✅ Validé par écran PAC |
| R112 = T° extérieure | ✅ Confirmé (8.3°C écran = 8.38°C Modbus) |
| R117 = T° sortie compresseur | ✅ Confirmé (47.9°C écran = 46.40°C Modbus) |
| Compteurs R90/R131 | ✅ Incrémentent en temps réel |

### Éléments non validés

| Élément | Statut |
|---------|--------|
| Seuils d'alerte (docs/registers.md) | Basés sur doc Aldes, non validés formellement |
| Codes erreur PAC | Non explorés, registres inconnus |
| Comportement mode Vacances (0x1234) | Placeholder, comportement exact non validé |
| Tests mode clim | Limités (conditions météo) |
| Composant ESPHome long terme | Non testé en conditions réelles |

### Bugs connus

1. **Collision bus RS485** : Si télécommande branchée en même temps que ESP32 → 2 maîtres sur le bus → erreurs CRC massives
2. **Valeur vacances 0x1234** : Fonctionne pour activer le mode mais comportement exact de la PAC non documenté

### Dashboard Home Assistant

Existe sur l'installation locale (Mushroom Cards, 5 onglets) mais pas encore exporté dans le repo. À ajouter si pertinent.

### Ce qui bloque la publication

- ~~Revalidation complète de tous les tests~~ ✅ Lecture complétée (2025-01-10)
- ~~Tests protocole 0x17 sniffing~~ ✅ X01-X20 complétés (2025-01-13)
- ~~Tests envoi trame 0x17 (Y01-Y07)~~ ✅ Validés via Pi 2B RS485 (2025-01-13)
- ~~Mise à jour composant ESPHome avec offsets corrigés~~ ✅ Complété (2025-01-13)
- Tests envoi ESP32 → PAC (validation finale sur hardware cible)
- Tests long terme du composant ESPHome

---

## Rappels pour l'IA

1. **Ne jamais suggérer** de modifier les consignes thermostats par logiciel - limitation hardware.
2. **Toujours rappeler** le statut BETA et les risques lors de modifications critiques.
3. **Préserver** la compatibilité avec le projet TOUG original quand possible.
4. **Documentation en français** pour les utilisateurs finaux.
5. **Respecter** le `.gitignore` - notamment `secrets.yaml`.
6. **Mettre à jour ce fichier** lors de découvertes importantes ou changements de structure.
