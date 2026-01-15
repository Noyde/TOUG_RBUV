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

### Offset 24-25 : Flag mode service

| Valeur hex | État |
|------------|------|
| 0x0000 | Mode normal |
| 0x3412 | Mode installateur/service |

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

| Pattern | Type | Description |
|---------|------|-------------|
| `01 17 80 0b` | Réponse longue | Contient l'état des bouches (bitmap) |
| `01 17 80 00` | Réponse courte | Données capteurs |
| `01 17 78 xx` | Réponse secondaire | Données additionnelles |

### Bitmap état des bouches (byte 33 de la réponse `01 17 80 0b`)

> ✅ **Découverte 2025-01-15** : L'état des bouches est accessible via le byte 33 de la réponse 0x17 !

| Bit | Zone | Valeur hex | LED |
|-----|------|------------|-----|
| 0 | K1a (Salon) | 0x01 | 1 |
| 1 | K1b (Cuisine) | 0x02 | 2 |
| 2 | K3 | 0x04 | 3 |
| 3 | K4 | 0x08 | 4 |
| 4 | K5 | 0x10 | 5 |
| 5 | K6 | 0x20 | 6 |

**Exemples :**
- K3 seule active → byte 33 = 0x04
- K4 seule active → byte 33 = 0x08
- K5 seule active → byte 33 = 0x10
- K3 + K4 actives → byte 33 = 0x0C (0x04 | 0x08)

### Comparaison avec registre R77 (USB)

| Méthode | Bus | Type | Limitation |
|---------|-----|------|------------|
| R77 via USB | USB 1200 | Index zone (0-5) | Dernière zone uniquement |
| Byte 33 réponse 0x17 | RS485 19200 | Bitmap | **Toutes les zones** ✓ |

> **Conclusion** : Pour connaître l'état de TOUTES les bouches simultanément, utiliser la réponse 0x17 sur RS485.
> Ceci élimine le besoin d'optocouplers pour la détection de l'état des bouches sur RBUV.

---

## 9. Avertissements

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

## 10. Ressources

| Ressource | Lien |
|-----------|------|
| Projet TOUG (djtef) | https://github.com/djtef/toug |
| Forum HACF | https://forum.hacf.fr/t/aldes-t-one-air-aquaair/42974 |
| Forum HACF - TOUG DefiDIY25 | https://forum.hacf.fr/t/defidiy25-toug-passerelle-esphome-pour-piloter-la-pac-aldes-t-one-sans-cloud-et-avec-routeur-solaire/68244 |

---

*Documentation TOUG_RBUV - Protocole 0x17*
