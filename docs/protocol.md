# Protocole 0x17 - Écriture sur PAC Aldes T.One RBUV

Documentation du protocole propriétaire utilisé pour l'écriture sur les anciens modèles T.One (2018 et antérieurs).

> ⚠️ **Important** : Ce protocole a été découvert par reverse engineering. Utilisez-le à vos risques.

---

## 1. Contexte

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

## 2. Structure de la trame (74 bytes)
```
Offset  Taille  Description                 Valeurs
------  ------  --------------------------  ------------------
0       1       Adresse Modbus              0x01
1       1       Fonction                    0x17
2-3     2       Sous-code séquence          0x00, 0x41/0x01/0x81/0xC1
4-5     2       Longueur                    0x00, 0x40
6-7     2       Constante                   0x00, 0x57
8-9     2       Constante                   0x00, 0x1F
10-11   2       Signature "sp"              0x73, 0x70
12-13   2       Version                     0x18, 0x04
14-17   4       Réservé                     0x00 x 4
18-19   2       Niveau (Eco/Confort/Boost)  Voir section 3
20-27   8       Padding                     0x00 x 8
28-29   2       Débit nominal               Valeur m3/h
30-31   2       PSE débit nominal           Valeur Pa
32-33   2       Débit mini / Vacances       Valeur m3/h ou flag
34-35   2       PSE mini / On-Off           Valeur Pa ou flag
36-37   2       Type mode (Chaud/Clim)      Voir section 3
38-39   2       Padding                     0x00, 0x00
40-69   30      Pattern fixe                Consignes (non modifiables)
70-71   2       Padding                     0x00, 0x00
72-73   2       CRC16 Modbus                Calculé sur bytes 0-71
```

---

## 3. Valeurs des champs de contrôle

### Offset 18-19 : Niveau

| Valeur hex | Mode |
|------------|------|
| 0x0000 | Confort |
| 0x00C8 | Eco |
| 0x5678 | Boost (Clim uniquement) |

### Offset 32-33 : Mode Vacances

| Valeur hex | État |
|------------|------|
| 0x0000 | Vacances Off |
| 0x1234 | Vacances On |

### Offset 34-35 : On/Off

| Valeur hex | État |
|------------|------|
| 0x0002 | Off |
| 0x0003 | On |

### Offset 36-37 : Type de mode

| Valeur hex | Mode |
|------------|------|
| 0x000C | Chauffage |
| 0x000A | Climatisation |

---

## 4. Modes pré-configurés

| Mode | Niveau (18-19) | Vacances (32-33) | On/Off (34-35) | Type (36-37) |
|------|----------------|------------------|----------------|--------------|
| **Chauffage Confort** | 0x0000 | 0x0000 | 0x0003 | 0x000C |
| **Chauffage Eco** | 0x00C8 | 0x0000 | 0x0003 | 0x000C |
| **Clim Confort** | 0x0000 | 0x0000 | 0x0003 | 0x000A |
| **Clim Boost** | 0x5678 | 0x0000 | 0x0003 | 0x000A |
| **Off** | 0x0000 | 0x0000 | 0x0002 | 0x000C |
| **Vacances** | 0x0000 | 0x1234 | 0x0003 | 0x000C |

---

## 5. Paramètres ventilation

Les offsets 28-35 peuvent aussi servir à modifier les paramètres de ventilation :

### Débit nominal (offset 28-29, registre R250)

Valeurs autorisées (m3/h) : 585, 600, 620, 640, 660, 680, 700, 720, 740, 760, 780, 800, 820, 840, 860, 880, 900

### PSE débit nominal (offset 30-31, registre R247)

Plage : 10 à 99 Pa (pas de 1 Pa)

### Débit mini 1 bouche (offset 32-33, registre R249)

Valeurs autorisées (m3/h) : 90, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 315

### PSE débit mini (offset 34-35, registre R248)

Plage : 8 à 80 Pa (pas de 1 Pa)

---

## 6. Correspondance Offset - Registre Modbus

| Offset trame | Registre | Paramètre |
|--------------|----------|-----------|
| 28-29 | R250 (0xFA) | Débit nominal |
| 30-31 | R247 (0xF7) | PSE débit nominal |
| 32-33 | R249 (0xF9) | Débit mini 1 bouche |
| 34-35 | R248 (0xF8) | PSE débit mini |

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

---

## 8. Avertissements

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

## 9. Ressources

| Ressource | Lien |
|-----------|------|
| Projet TOUG (djtef) | https://github.com/djtef/toug |
| Forum HACF | https://forum.hacf.fr/t/aldes-t-one-air-aquaair/42974 |
| Forum HACF - TOUG DefiDIY25 | https://forum.hacf.fr/t/defidiy25-toug-passerelle-esphome-pour-piloter-la-pac-aldes-t-one-sans-cloud-et-avec-routeur-solaire/68244 |

---

*Documentation TOUG_RBUV - Protocole 0x17*
