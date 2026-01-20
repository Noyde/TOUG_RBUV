# Protocole 0x17 - Écriture sur PAC Aldes T.One RBUV

Documentation du protocole propriétaire utilisé pour l'écriture sur les anciens modèles T.One (2018 et antérieurs).

> ⚠️ **Important** : Ce protocole a été découvert par reverse engineering. Utilisez-le à vos risques.

---

## 1. Contexte

### Rôle du protocole 0x17

Le protocole 0x17 permet de contrôler **uniquement les MODES de la PAC** :
- État On/Off
- Type de mode (Chauffage / Climatisation / Service)
- Niveau Eco/Confort
- Boost (Clim uniquement)
- Mode Vacances
- Paramètres ventilation (débit nominal, PSE)

> **IMPORTANT** : Le protocole 0x17 **NE contrôle PAS** la régulation des zones (ouverture/fermeture des bouches motorisées).
> Les thermostats 868MHz communiquent **directement** avec le régulateur PAC, indépendamment des trames 0x17.
> **Validé 2025-01-13** : Les bouches réagissent aux thermostats même sans télécommande et sans trames 0x17.

### Pourquoi un protocole spécial ?

Les modèles T.One RBUV (2018) n'acceptent pas les fonctions Modbus standard pour l'écriture :

| Fonction | Code | Résultat |
|----------|------|----------|
| Write Single Register | 0x06 | `illegal data address` |
| Write Multiple Registers | 0x10 | `illegal data address` |
| Read/Write Multiple | 0x17 | ✅ **Fonctionne** |

La télécommande Aldes utilise la fonction **0x17** (Read/Write Multiple Registers) avec une trame de 74 bytes.

### Bus de communication

| Bus | Baudrate | Lecture | Écriture 0x17 |
|-----|----------|---------|---------------|
| USB | 1200 | ✅ | ❌ |
| Télécommande (RS485) | 19200 | ✅ | ✅ |

L'écriture via protocole 0x17 ne fonctionne que sur le **bus télécommande** (RS485, 19200 bauds).

---

## 2. Structure de la trame (74 bytes) - VALIDÉ 2025-01-13

> ⚠️ **Structure validée par sniffing télécommande** (tests X01-X20)

| Offset | Taille | Description | Valeurs |
|--------|--------|-------------|---------|
| 0 | 1 | Adresse Modbus | 0x01 |
| 1 | 1 | Fonction | 0x17 |
| 2-3 | 2 | Sous-code séquence | Cycle: 0x0001→0x0041→0x0081→0x00C1 |
| 4-5 | 2 | Longueur | 0x0040 (64) |
| 6-7 | 2 | Constante | 0x0057 |
| 8-9 | 2 | Constante | 0x001F |
| 10-11 | 2 | Signature "sp" | 0x7370 |
| 12-13 | 2 | Version | 0x1804 |
| 14-15 | 2 | Compteur | Incrémente à chaque trame |
| 16-17 | 2 | Réservé | 0xF67A observé |
| **18-19** | 2 | **Niveau** | 0x0000=Confort, 0x00C8=Eco |
| **20-21** | 2 | **Boost** | 0x0000=Normal, 0x5678=Boost |
| 22-23 | 2 | Padding | 0x0000 |
| **24-25** | 2 | **Flag mode service** | 0x0000=Normal, 0x3412=Installateur |
| **26-27** | 2 | **Débit nominal** | m³/h (ex: 0x0384=900) |
| **28-29** | 2 | **PSE nominal** | Pa (ex: 0x0017=23) |
| **30-31** | 2 | **Débit 1 bouche** | m³/h (ex: 0x00F0=240) |
| **32-33** | 2 | **PSE mini** | Pa (ex: 0x000C=12) |
| **34-35** | 2 | **Vacances** | 0x0000=Off, 0x1234=On |
| **36-37** | 2 | **On/Off** | 0x0002=Off, 0x0003=On |
| **38-39** | 2 | **Type mode** | 0x000A=Clim, 0x000B=Service, 0x000C=Chauffage |
| 40-69 | 30 | Consignes zones | Pattern 0x7FFE = pas de changement |
| 70-71 | 2 | Padding | 0x0000 |
| 72-73 | 2 | CRC16 Modbus | Calculé sur bytes 0-71 |

---

## 3. Valeurs des champs de contrôle

### Offset 18-19 : Niveau (Eco/Confort)

| Valeur hex | Mode |
|------------|------|
| 0x0000 | Confort |
| 0x00C8 | Eco |

### Offset 20-21 : Boost

| Valeur hex | Mode |
|------------|------|
| 0x0000 | Normal |
| 0x5678 | Boost (Clim uniquement) |

### Offset 24-25 : Flag mode service - CONFIRMÉ 2025-01-18

> ✅ **Confirmé** via capture sniff_X11.bin (test modification débit nominal)

| Valeur hex | État |
|------------|------|
| 0x0000 | Mode normal |
| **0x3412** | **Mode installateur/service** |

**Note** : Ce flag est envoyé **conjointement** avec le type mode 0x000B (offset 38-39) lors de modifications des paramètres de ventilation via le menu installateur de la télécommande.

### Offset 34-35 : Mode Vacances

| Valeur hex | État |
|------------|------|
| 0x0000 | Vacances Off |
| 0x1234 | Vacances On |

### Offset 36-37 : On/Off

| Valeur hex | État |
|------------|------|
| 0x0002 | Off |
| 0x0003 | On |

### Offset 38-39 : Type de mode

| Valeur hex | Mode |
|------------|------|
| 0x000A | Climatisation |
| 0x000B | Service/Installateur |
| 0x000C | Chauffage |

---

## 4. Modes pré-configurés

| Mode | Niveau (18-19) | Boost (20-21) | Vacances (34-35) | On/Off (36-37) | Type (38-39) |
|------|----------------|---------------|------------------|----------------|--------------|
| **Chauffage Confort** | 0x0000 | 0x0000 | 0x0000 | 0x0003 | 0x000C |
| **Chauffage Eco** | 0x00C8 | 0x0000 | 0x0000 | 0x0003 | 0x000C |
| **Clim Confort** | 0x0000 | 0x0000 | 0x0000 | 0x0003 | 0x000A |
| **Clim Boost** | 0x0000 | 0x5678 | 0x0000 | 0x0003 | 0x000A |
| **Off** | 0x0000 | 0x0000 | 0x0000 | 0x0002 | 0x000C |
| **Vacances** | 0x0000 | 0x0000 | 0x1234 | 0x0003 | 0x000C |

---

## 5. Paramètres ventilation

Les offsets 26-33 servent à modifier les paramètres de ventilation (mode installateur) :

### Débit nominal (offset 26-27, registre R250)

Valeurs autorisées (m³/h) : 585-900 (pas de 20)
Exemple : 0x0384 = 900, 0x0370 = 880, 0x0348 = 840

### PSE débit nominal (offset 28-29, registre R247)

Plage : 10 à 99 Pa (pas de 1 Pa)
Exemple : 0x0017 = 23, 0x0018 = 24

### Débit mini 1 bouche (offset 30-31, registre R249)

Valeurs autorisées (m³/h) : 90-315 (pas de 20)
Exemple : 0x00F0 = 240, 0x00DC = 220

### PSE débit mini (offset 32-33, registre R248)

Plage : 8 à 80 Pa (pas de 1 Pa)
Exemple : 0x000C = 12, 0x000B = 11

---

## 6. Correspondance Offset - Registre Modbus

| Offset trame | Registre | Paramètre |
|--------------|----------|-----------|
| 26-27 | R250 (0xFA) | Débit nominal |
| 28-29 | R247 (0xF7) | PSE débit nominal |
| 30-31 | R249 (0xF9) | Débit mini 1 bouche |
| 32-33 | R248 (0xF8) | PSE débit mini |

---

## 7. Limitations connues

### Consignes thermostats : NON MODIFIABLES

Les registres R20-R25 (consignes thermostats) sont **hardware read-only** sur le modèle 2018. Ils sont pilotés exclusivement par les thermostats radio 868MHz et ne peuvent pas être modifiés via :
- Modbus standard (0x06, 0x10)
- Protocole 0x17
- Registres TOUG 31100-31104 (non implémentés)

### Programmes horaires

Les programmes horaires sont stockés localement dans la télécommande Aldes. La télécommande envoie le mode courant (Confort/Eco) quand l'heure programmée arrive.

Pour gérer les horaires via domotique : utiliser les automatisations Home Assistant.

### Date/heure : NON TRANSMISE

La date/heure n'est **pas encodée** dans les trames 0x17 (validé par tests X19-X20).
Chaque appareil (télécommande, PAC) maintient sa propre horloge indépendamment.

Les registres R16/R17 (date/heure via USB) ne fonctionnent pas sur RBUV.

---

## 8. Structure de la réponse PAC (133 bytes) - VALIDÉ 2025-01-15

La PAC répond aux trames 0x17 avec une réponse de 133 bytes contenant des informations capteurs et l'état des bouches.

### Types de réponse

| Pattern | Type | Taille | Description |
|---------|------|--------|-------------|
| `01 17 80 0b` | Réponse principale | ~133 bytes | Zones, thermostats, **R60-R64** ✅ |
| `01 17 80 01` | Réponse compresseur | ~130 bytes | **R65 Consigne fréq, R117 T° sortie** ✅ VALIDÉ |
| `01 17 80 00` | Réponse courte | ~129 bytes | Données capteurs |
| `01 17 78 xx` | Réponse ventilation | ~128 bytes | **R247-R251 Débits/PSE** ✅ VALIDÉ |

### Structure détaillée réponse `01 17 80 0b` (133 bytes)

> ✅ **VALIDÉ 2025-01-20** : Structure confirmée par capture synchronisée (RS485 + USB simultanés)

| Offset | Taille | Description | Valeurs | Statut |
|--------|--------|-------------|---------|--------|
| 0 | 1 | Adresse Modbus | 0x01 | ✅ Confirmé |
| 1 | 1 | Fonction | 0x17 | ✅ Confirmé |
| 2 | 1 | Type réponse | 0x80 | ✅ Confirmé |
| 3 | 1 | Sous-type | 0x0B | ✅ Confirmé |
| 4 | 1 | Compteur | Incrémente | ✅ Confirmé |
| **5-6** | 2 | **R62** | big-endian | ✅ **VALIDÉ 2025-01-20** |
| **7-8** | 2 | **R63** | big-endian | ✅ **VALIDÉ 2025-01-20** |
| 9-19 | 11 | ? | Variable | ❓ À identifier |
| **20** | 1 | **Mode PAC** | 02=Clim, 04=Chauff, 05=Off | ✅ Confirmé |
| 21-32 | 12 | ? | Variable | ❓ À identifier |
| **33** | 1 | **Bitmap bouches** | Voir tableau ci-dessous | ✅ **Confirmé** |
| 34-41 | 8 | ? | Variable | ❓ À identifier |
| **42-53** | 12 | **Consignes zones (R20-R25)** | 6×2 bytes, big-endian, ÷100 pour °C | ✅ **VALIDÉ 2025-01-20** |
| 54-73 | 20 | ? | Variable | ❓ À identifier |
| **74-85** | 12 | **T° zones mesurées (R36-R41)** | 6×2 bytes, big-endian, ÷100 pour °C | ✅ **VALIDÉ 2025-01-20** |
| 86-88 | 3 | ? | Variable | ❓ À identifier |
| **89-112** | 24 | **IDs thermostats 868MHz** | 6×4 bytes, little-endian | ✅ **Confirmé** |
| 113-120 | 8 | Padding | 0xFFFFFFFFFFFFFFFF | ✅ Confirmé |
| **121-122** | 2 | **R60 Fréquence compresseur** | big-endian, ÷10 Hz | ✅ **VALIDÉ 2025-01-20** |
| **123-124** | 2 | **R61 Vitesse ventilation** | big-endian, rpm | ✅ **VALIDÉ 2025-01-20** |
| **125-126** | 2 | **R62** | big-endian | ✅ **VALIDÉ 2025-01-20** |
| **127-128** | 2 | **R63** | big-endian | ✅ **VALIDÉ 2025-01-20** |
| **129-130** | 2 | **R64** | big-endian | ✅ **VALIDÉ 2025-01-20** |
| 131-132 | 2 | CRC16 Modbus | Calculé | ✅ Confirmé |

### Bitmap état des bouches (byte 33)

> ✅ **Découverte 2025-01-15** : L'état des bouches est accessible via le byte 33 de la réponse 0x17 !

| Bit | Zone | Valeur hex | LED |
|-----|------|------------|-----|
| 0 | K1a (Salon) | 0x01 | 1 |
| 1 | K1b (Cuisine) | 0x02 | 2 |
| 2 | K3 | 0x04 | 3 |
| 3 | K4 | 0x08 | 4 |
| 4 | K5 | 0x10 | 5 |
| 5 | K6 | 0x20 | 6 |

**Exemples validés :**
- K1a + K1b actives → byte 33 = 0x03 (0x01 | 0x02) ✅
- K4 seule active → byte 33 = 0x08 ✅
- K5 seule active → byte 33 = 0x10 ✅
- K3 + K4 actives → byte 33 = 0x0C (0x04 | 0x08)

### IDs thermostats 868MHz (offsets 89-112)

> ✅ **Découverte 2025-01-18** : Les IDs des thermostats radio sont transmis dans la réponse !

Format : 6 IDs de 4 bytes chacun, encodés en **little-endian**.

| Offset | Zone | Exemple hex | ID décimal |
|--------|------|-------------|------------|
| 89-92 | TH1 (K1a) | `e7 87 00 f3` | 00F3E787 |
| 93-96 | TH2 (K1b) | `e7 87 00 f3` | 00F3E787 |
| 97-100 | TH3 (K3) | `03 e2 00 f3` | 00F3E203 |
| 101-104 | TH4 (K4) | `e3 e1 00 f3` | 00F3E1E3 |
| 105-108 | TH5 (K5) | `fe e1 00 f3` | 00F3E1FE |
| 109-112 | TH6 (K6) | `e0 e1 00 f3` | 00F3E1E0 |

> **Note** : TH1 et TH2 partagent le même ID car K1a et K1b sont sur le même thermostat physique.

### Validation capture synchronisée (2025-01-20)

Capture RS485 et lecture Modbus USB effectuées simultanément. **Correspondance parfaite !**

#### Consignes zones (offsets 42-53)

| Zone | Offset | Trame 0x17 | R20-R25 USB | Match |
|------|--------|------------|-------------|-------|
| Z1 (K1a) | 42-43 | **21.00°C** | **2100** | ✅ |
| Z1b (K1b) | 44-45 | **21.00°C** | **2100** | ✅ |
| Z2 | 46-47 | **19.00°C** | **1900** | ✅ |
| Z3 | 48-49 | **21.00°C** | **2100** | ✅ |
| Z4 | 50-51 | **20.00°C** | **2000** | ✅ |
| Z5 | 52-53 | **20.00°C** | **2000** | ✅ |

#### Températures zones (offsets 74-85)

| Zone | Offset | Trame 0x17 | R36-R41 USB | Match |
|------|--------|------------|-------------|-------|
| Z1 (K1a) | 74-75 | **21.18°C** | **2118** | ✅ |
| Z1b (K1b) | 76-77 | **21.18°C** | **2118** | ✅ |
| Z2 | 78-79 | **19.75°C** | **1975** | ✅ |
| Z3 | 80-81 | **21.75°C** | **2175** | ✅ |
| Z4 | 82-83 | **20.00°C** | **2000** | ✅ |
| Z5 | 84-85 | **20.00°C** | **2000** | ✅ |

> **Conclusion** : Structure de la réponse `01 17 80 0b` entièrement validée par capture synchronisée !

### Structure réponse `01 17 80 01` (Compresseur + Système) - VALIDÉ 2025-01-20

> ✅ **Découverte 2025-01-20** : La réponse `80 01` contient R65 (consigne fréq), R104-R112 (système), R117 (T° compresseur) !

| Offset | Taille | Description | Registre | Format | Statut |
|--------|--------|-------------|----------|--------|--------|
| 0-3 | 4 | Header | 01 17 80 01 | - | ✅ |
| **4-5** | 2 | **Consigne fréquence** | **R65** | little-endian, ÷10 Hz | ✅ **VALIDÉ** |
| 6-81 | 76 | Données diverses | ? | - | ❓ À identifier |
| **82-83** | 2 | **?** | **R104** | big-endian | ✅ **VALIDÉ** |
| **84-85** | 2 | **?** | **R105** | big-endian | ✅ **VALIDÉ** |
| **86-87** | 2 | **?** | **R106** | big-endian | ✅ **VALIDÉ** |
| **88-89** | 2 | **?** | **R107** | big-endian | ✅ **VALIDÉ** |
| **90-91** | 2 | **?** | **R108** | big-endian | ✅ **VALIDÉ** |
| **92-93** | 2 | **?** | **R109** | big-endian | ✅ **VALIDÉ** |
| **94-95** | 2 | **?** | **R110** | big-endian | ✅ **VALIDÉ** |
| **96-97** | 2 | **Température ?** | **R111** | big-endian, ÷100 °C | ✅ **VALIDÉ** |
| **98-99** | 2 | **T° extérieure** | **R112** | big-endian, ÷100 °C | ✅ **VALIDÉ** |
| 100-104 | 5 | Données diverses | ? | - | ❓ À identifier |
| **~105-106** | 2 | **T° sortie compresseur** | **R117** | big-endian, ÷100 °C | ✅ **VALIDÉ** |

#### Validation capture synchronisée (2025-01-20)

| Paramètre | R USB | Capture hex | Valeur | Match |
|-----------|-------|-------------|--------|-------|
| Consigne fréquence | R65=310 | 0x36 0x01 | 31.0 Hz | ✅ |
| T° sortie compresseur | R117=4866 | 0x13 0x02 | 48.66°C | ✅ |

#### Registres système R104-R112 (offsets 82-99) - VALIDÉ 2025-01-20

| Offset | Hex exemple | Valeur | Registre | Description |
|--------|-------------|--------|----------|-------------|
| 82-83 | 00 bf | 191 | R104 | ? |
| 84-85 | 00 00 | 0 | R105 | ? |
| 86-87 | 00 05 | 5 | R106 | ? |
| 88-89 | 00 81 | 129 | R107 | ? |
| 90-91 | 00 20 | 32 | R108 | ? |
| 92-93 | 00 7c | 124 | R109 | ? |
| 94-95 | 00 ff | 255 | R110 | ? |
| 96-97 | 08 82 | 2178 | R111 | **21.78°C = T° air repris UI** |
| 98-99 | 03 14 | 788 | R112 | **7.88°C = T° extérieure** |

> **Note** :
> - R111 = Température air repris UI (air de retour vers l'unité intérieure)
> - R112 = T° extérieure. Sur modèle RBUV sans ECS, ce registre contient la température extérieure (pas la sonde ECS comme sur modèles avec ballon).

### Structure réponse `01 17 78 xx` (Ventilation) - VALIDÉ 2025-01-20

> ✅ **Découverte 2025-01-20** : Les paramètres de ventilation (R247-R251) sont dans la réponse `78 xx`, pas `80 0b` !

La réponse `78 xx` contient les données de ventilation et compresseur. Taille ~128 bytes.

#### Paramètres ventilation (offsets ~107-118)

| Offset | Taille | Description | Registre | Format | Statut |
|--------|--------|-------------|----------|--------|--------|
| ~107-108 | 2 | ? | ? | big-endian | ❓ |
| **~109-110** | 2 | **PSE Nominal** | **R247** | big-endian | ✅ **VALIDÉ** |
| **~111-112** | 2 | **PSE Mini** | **R248** | big-endian | ✅ **VALIDÉ** |
| **~113** | 1 | **Débit 1 Bouche** | **R249** | 8-bit | ✅ **VALIDÉ** |
| **~114-115** | 2 | **Débit Nominal** | **R250** | big-endian | ✅ **VALIDÉ** |
| **~116-117** | 2 | **PSE Mesurée** | **R251** | big-endian | ✅ **VALIDÉ** |

#### Validation capture synchronisée (2025-01-20)

| Paramètre | Dashboard | R USB | Capture hex | Match |
|-----------|-----------|-------|-------------|-------|
| PSE Nominal | 23 Pa | R247=23 | 0x0017 | ✅ |
| PSE Mini | 12 Pa | R248=12 | 0x000C | ✅ |
| Débit 1 Bouche | 240 m³/h | R249=240 | 0xF0 | ✅ |
| Débit Nominal | 900 m³/h | R250=900 | 0x0384 | ✅ |
| PSE Mesurée | 15 Pa | R251=15 | 0x000F | ✅ |

#### Résumé des registres par type de réponse

| Registre | Description | Réponse | Offset | Statut |
|----------|-------------|---------|--------|--------|
| **R60** | **Fréquence compresseur** | `80 0b` | 121-122 | ✅ **VALIDÉ** |
| R61 | Vitesse ventilation | `80 0b` | 123-124 | ✅ VALIDÉ |
| R62 | ? | `80 0b` | 5-6, 125-126 | ✅ VALIDÉ |
| R63 | ? | `80 0b` | 7-8, 127-128 | ✅ VALIDÉ |
| R64 | ? | `80 0b` | 129-130 | ✅ VALIDÉ |
| R65 | Consigne fréquence | `80 01` | 4-5 | ✅ VALIDÉ |
| **R104-R110** | **Données système** | `80 01` | 82-95 | ✅ **VALIDÉ** |
| **R111** | **T° air repris UI** | `80 01` | 96-97 | ✅ **VALIDÉ** |
| **R112** | **T° extérieure** | `80 01` | 98-99 | ✅ **VALIDÉ** |
| R117 | T° sortie compresseur | `80 01` | ~105-106 | ✅ VALIDÉ |
| R247 | PSE Nominal | `78 xx` | ~109-110 | ✅ VALIDÉ |
| R248 | PSE Mini | `78 xx` | ~111-112 | ✅ VALIDÉ |
| R249 | Débit 1 Bouche | `78 xx` | ~113 | ✅ VALIDÉ |
| R250 | Débit Nominal | `78 xx` | ~114-115 | ✅ VALIDÉ |
| R251 | PSE Mesurée | `78 xx` | ~116-117 | ✅ VALIDÉ |

> **Note** : Tous les registres compresseur/ventilation/système (R60-R65, R104-R112, R117, R247-R251) sont maintenant localisés !

### Comparaison avec registre R77 (USB)

| Méthode | Bus | Type | Limitation |
|---------|-----|------|------------|
| R77 via USB | USB 1200 | Index zone (0-5) | Dernière zone uniquement |
| Byte 33 réponse 0x17 | RS485 19200 | Bitmap | **Toutes les zones** ✓ |

> **Conclusion** : Pour connaître l'état de TOUTES les bouches simultanément, utiliser la réponse 0x17 sur RS485.
> Ceci élimine le besoin d'optocouplers pour la détection de l'état des bouches sur RBUV.

### Données écran PAC (référence pour validation)

Valeurs observées sur écran TEST PAC et REGLAGE DEBIT/PRESSION UI :

| Paramètre | Valeur | Hex attendu | Registre Modbus |
|-----------|--------|-------------|-----------------|
| Nb. heures comp. ON | 12400 H | 0x3070 | R66 |
| Tsortie Comp. | 61,7 °C | 0x1829 (÷100) | R117 |
| Tair exterieur | 2,0 °C | 0x00C8 (÷100) | R112 |
| Tair repris UI | 6,2 °C | 0x026C (÷100) | ? |
| EEV1 | 110 Pls | 0x006E | R64 |
| Nb. canaux ON | 3 | 0x03 | ? |
| Debit aux bouches | 301 m³/h | 0x012D | R251 |
| P. statique externe | 13 Pa | 0x000D | R247 |

> Ces valeurs serviront de référence pour valider les offsets lors d'une capture synchronisée.

### Méthodologie de mapping des bytes inconnus

Pour identifier les bytes inconnus de la réponse, suivre cette procédure :

1. **Capture synchronisée** : Capturer les trames RS485 pendant que l'écran PAC affiche des valeurs connues
2. **Varier un seul paramètre** : Changer une seule condition (ex: allumer/éteindre une zone)
3. **Comparer les trames** : Identifier les bytes qui changent entre les captures
4. **Corrélation** : Vérifier si les valeurs correspondent aux données écran (÷100 pour °C, ÷10 pour Hz)

### Bytes à investiguer en priorité

| Offset | Hypothèse | Test suggéré |
|--------|-----------|--------------|
| 5-6 | Débit mesuré | Comparer avec R251 |
| 7-8 | PSE mesurée | Comparer avec R247 |
| 13-14 | Compteur trame | Vérifier incrémentation |
| 34-38 | État compresseur ? | Comparer On/Off compresseur |
| 51-68 | T° supplémentaires ? | Comparer avec R104-R117 |
| 81-84 | Fréquences ? | Comparer avec R60-R63 |

### Exemple d'analyse capture_zones.bin

Extrait typique d'une réponse `80 0b` (hexdump) :

```
0117 800b cb00 0000 0000 0000 0000 0000  # Header + données début
0000 0000 0400 0000 0000 0000 0000 0808  # Mode=04 (chauffage), bitmap=08 (K4)
1508 0a08 1508 1508 1508 1508 0000 0000  # Consignes zones?
...
e787 00f3 e787 00f3 e203 00f3 e1e3 00f3  # IDs thermostats TH1-TH4
e1fe 00f3 e1e0 00f3 0000 0000 0000 0000  # IDs TH5-TH6 + padding
xxxx                                      # CRC16
```

> **Note** : Les valeurs réelles varient selon l'état de la PAC au moment de la capture.

---

## 9. Trame `21 xx` - Communication interne PAC - DÉCOUVERTE 2025-01-20

> ⚠️ **DÉCOUVERTE** : Une trame différente de `01 17` a été identifiée sur le bus RS485 !

Cette trame semble être une communication interne de la PAC (pas initiée par la télécommande). Elle contient :
- **Courant compresseur** - ⚠️ **SEULE SOURCE FIABLE** (R49 USB = valeur incorrecte)
- Heures compresseur/ventilateur (aussi dispo via R125/R127 USB)
- Températures internes (aussi dispo via R111-R117 USB)

### Caractéristiques

| Propriété | Valeur |
|-----------|--------|
| Pattern | `21 xx ...` (pas `01 17`) |
| Bus | RS485 télécommande (19200 bauds) |
| Périodicité | Communication interne périodique |

### Structure identifiée (partielle)

> ✅ **Valeurs confirmées** par comparaison avec écran télécommande

| Offset | Taille | Description | Format | Équiv. USB | Statut |
|--------|--------|-------------|--------|------------|--------|
| 56 | 1 | Niveau ventil UE | entier | R106 | ✅ **VALIDÉ** |
| 62-63 | 2 | T° air repris UI | ÷100 °C | R111 | ✅ VALIDÉ |
| 64-65 | 2 | T° extérieure | ÷100 °C | R112 | ✅ VALIDÉ |
| 66-67 | 2 | T° échangeur UI | ÷100 °C | R114 | ✅ VALIDÉ |
| 68-69 | 2 | T° échangeur UE | ÷100 °C | R115 | ✅ VALIDÉ |
| 72-73 | 2 | T° ? | ÷100 °C | ? | ❓ À confirmer |
| **84-85** | 2 | **Courant compresseur** | ÷100 A | ❌ R49 KO | ✅ **UNIQUE** |
| 90-91 | 2 | Heures ventilateur | heures | R125 | ✅ VALIDÉ |
| 94-95 | 2 | Heures compresseur | heures | R127 | ✅ VALIDÉ |

### Validation courant compresseur (offsets 84-85)

| Capture | Écran télécommande | Hex trame | Valeur calculée | Match |
|---------|-------------------|-----------|-----------------|-------|
| #1 | **3.5 A** | 0x0164 | 356 ÷ 100 = 3.56 A | ✅ |
| #2 | **4.1 A** | 0x019A | 410 ÷ 100 = 4.10 A | ✅ |

### Validation heures (offsets 90-95)

| Paramètre | Dashboard | Hex trame | Valeur | Match |
|-----------|-----------|-----------|--------|-------|
| Heures ventilateur | ~25500 h | 0x639C | 25500 | ✅ |
| Heures compresseur | 12700 h | 0x319C | 12700 | ✅ |

### Importance de cette découverte

Le **courant compresseur** n'est disponible **nulle part ailleurs** :
- ❌ USB Modbus (R49 = valeur incorrecte)
- ❌ Réponse `01 17 80 xx`
- ✅ **Uniquement dans la trame `21 xx`**

---

## Résumé : Valeurs UNIQUES au RS485 (non dispo USB)

> ⚠️ **Ces 3 valeurs justifient l'utilisation du bus RS485 plutôt que USB !**

| Valeur | USB Modbus | RS485 | Réponse/Trame |
|--------|------------|-------|---------------|
| **Bitmap bouches actives** | ❌ R77=index, R5029=0 | ✅ Byte 33 | `01 17 80 0b` |
| **Courant compresseur** | ❌ R49=243 (faux) | ✅ Offset 84-85 | Trame `21 xx` |
| **IDs thermostats 868MHz** | ❌ Non disponible | ✅ Offsets 89-112 | `01 17 80 0b` |

### Bitmap bouches (byte 33 réponse `80 0b`)
```
K1a=0x01, K1b=0x02, K3=0x04, K4=0x08, K5=0x10, K6=0x20
```
Exemple : K1a + K4 actives → byte 33 = 0x09 (0x01 | 0x08)

### Bytes à investiguer

| Offset | Hypothèse | Test suggéré |
|--------|-----------|--------------|
| 70-73 | T° sortie compresseur ? | Chercher valeur ~7000 (70°C) |
| 58-61 | Fréquences ? | Comparer avec R60/R65 |
| 76-83 | EEV / Pressions ? | Comparer avec R64/R104-R105 |

---

## 10. Avertissements

**Utilisation à vos risques**

- Ce protocole a été découvert par reverse engineering
- Il n'est pas documenté officiellement par Aldes
- Des erreurs dans les trames peuvent provoquer des comportements imprévus
- Faites des sauvegardes de vos configurations avant tests

**Cohabitation télécommande impossible**

L'ESP32 et la télécommande Aldes ne peuvent pas coexister sur le même bus RS485 :
- Les deux sont des maîtres Modbus
- Collisions garanties = erreurs CRC massives
- Solution : débrancher la télécommande quand l'ESP32 est utilisé

---

## 11. Ressources

| Ressource | Lien |
|-----------|------|
| Projet TOUG (djtef) | https://github.com/djtef/toug |
| Forum HACF | https://forum.hacf.fr/t/aldes-t-one-air-aquaair/42974 |
| Forum HACF - TOUG DefiDIY25 | https://forum.hacf.fr/t/defidiy25-toug-passerelle-esphome-pour-piloter-la-pac-aldes-t-one-sans-cloud-et-avec-routeur-solaire/68244 |

---

*Documentation TOUG_RBUV - Protocole 0x17*
