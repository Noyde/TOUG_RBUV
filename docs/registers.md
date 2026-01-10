# Registres Modbus - PAC Aldes T.One RBUV

Documentation des registres Modbus accessibles en lecture via USB.

> ⚠️ **Limitation modèle 2018** : L'écriture via USB retourne `illegal data address`. Seule la lecture est possible.

---

## Communication

| Paramètre | Valeur |
|-----------|--------|
| **Port** | USB (Mini-USB sur la PAC) |
| **Baudrate** | 1200 |
| **Parité** | EVEN |
| **Stop bits** | 1 |
| **Adresse Modbus** | 0x01 |
| **Fonction** | 0x03 (Read Holding Registers) |

---

## Système

| Registre | Nom | Unité | Diviseur | Notes |
|----------|-----|-------|----------|-------|
| 1 | Version Firmware | - | 1 | |
| 3 | Durée ON | min | 1 | Temps depuis dernier démarrage |
| 9 | Mode PAC | - | 1 | Voir tableau modes |

### Modes PAC (Registre 9)

| Code | Mode |
|------|------|
| 2 | Rafraîchissement |
| 4 | Chauffage |
| 5 | Off |

---

## Thermostats - Consignes (R20-R25)

| Registre | Hex | Zone | Unité | Diviseur |
|----------|-----|------|-------|----------|
| 20 | 0x14 | Zone 1 | °C | ÷100 |
| 21 | 0x15 | Zone 2 | °C | ÷100 |
| 22 | 0x16 | Zone 3 | °C | ÷100 |
| 23 | 0x17 | Zone 4 | °C | ÷100 |
| 24 | 0x18 | Zone 5 | °C | ÷100 |
| 25 | 0x19 | Zone 6 | °C | ÷100 |

> **Note** : Les consignes sont pilotées par les thermostats radio 868MHz et sont en lecture seule via Modbus.

---

## Thermostats - Températures (R36-R41)

| Registre | Hex | Zone | Unité | Diviseur | Signé |
|----------|-----|------|-------|----------|-------|
| 36 | 0x24 | Zone 1 | °C | ÷100 | Oui |
| 37 | 0x25 | Zone 2 | °C | ÷100 | Oui |
| 38 | 0x26 | Zone 3 | °C | ÷100 | Oui |
| 39 | 0x27 | Zone 4 | °C | ÷100 | Oui |
| 40 | 0x28 | Zone 5 | °C | ÷100 | Oui |
| 41 | 0x29 | Zone 6 | °C | ÷100 | Oui |

---

## Ventilation

| Registre | Nom | Unité | Diviseur |
|----------|-----|-------|----------|
| 60 | Consigne Ventilateur | rpm | 1 |
| 61 | Vitesse Ventilateur | rpm | 1 |
| 106 | Niveau Ventilation UE | - | 1 |
| 125 | Heures Ventilateur UI | h | 1 |

---

## Compresseur

| Registre | Nom | Unité | Diviseur | Notes |
|----------|-----|-------|----------|-------|
| 65 | Consigne Fréquence | Hz | ÷10 | |
| 66 | Fréquence Compresseur | Hz | ÷10 | |
| 127 | Heures Compresseur | h | 1 | Compteur total |

---

## Températures PAC internes

| Registre | Nom | Unité | Diviseur | Signé |
|----------|-----|-------|----------|-------|
| 111 | Temp Air Repris UI | °C | ÷100 | Oui |
| 112 | Temp Extérieure | °C | ÷100 | Oui |
| 114 | Temp Échangeur UI | °C | ÷100 | Oui |
| 115 | Temp Échangeur UE | °C | ÷100 | Oui |
| 117 | Temp Sortie Compresseur | °C | ÷100 | Non |

> **Note** : Les registres signés (S_WORD) permettent les valeurs négatives (hiver).

---

## Vannes EEV (Détendeurs électroniques)

| Registre | Nom | Unité | Diviseur |
|----------|-----|-------|----------|
| 104 | EEV1 | Pls | 1 |
| 105 | EEV2 | Pls | 1 |

---

## Compteurs / Timers

| Registre | Nom | Unité | Notes |
|----------|-----|-------|-------|
| 90 | Timer compresseur (?) | sec | Compteur incrémental, usage exact inconnu |
| 131 | Timer dégivrage (?) | sec | Temps depuis dernier dégivrage (hypothèse) |

> **Note** : R90 et R131 sont des compteurs en secondes. Leur signification exacte reste à confirmer.

---

## Débits / Pressions

| Registre | Hex | Nom | Unité | Diviseur |
|----------|-----|-----|-------|----------|
| 247 | 0xF7 | PSE Débit Nominal | Pa | 1 |
| 248 | 0xF8 | PSE Débit Mini | Pa | 1 |
| 249 | 0xF9 | Débit 1 Bouche | m³/h | 1 |
| 250 | 0xFA | Débit Nominal | m³/h | 1 |
| 251 | 0xFB | Pression Statique Ext | Pa | 1 |

---

## Seuils d'alerte (T.One AIR 04)

| Paramètre | Normal | Attention | Critique |
|-----------|--------|-----------|----------|
| Fréquence Compresseur | 20-70 Hz | >70 Hz | >90 Hz |
| T° Sortie Compresseur | 40-70°C | >80°C | >100°C |
| Vitesse Ventilateur | 300-600 rpm | >700 rpm | >800 rpm |
| Pression Statique | 15-50 Pa | >60 Pa | >80 Pa |
| EEV | 100-400 Pls | <50 / >450 | <20 / >480 |

---

## Différences TOUG vs RBUV

> ⚠️ **Important** : Le mapping des registres diffère selon le modèle (avec/sans ECS).

Le modèle RBUV n'a pas d'ECS (Eau Chaude Sanitaire). Certains registres sont donc réassignés :

| Registre | TOUG (avec ECS) | RBUV (sans ECS) |
|----------|-----------------|-----------------|
| **R39** | T° extérieure (ThoA) | T° Zone 4 |
| **R44** | T° sortie compresseur | ❌ Non implémenté (592°C) |
| **R112** | Sonde ECS bas | **T° extérieure** |
| **R117** | Échangeur air capillaire Th6 | **T° sortie compresseur** |

### Registres TOUG non disponibles sur RBUV

| Registre | Description TOUG | Statut RBUV |
|----------|------------------|-------------|
| R44 | T° sortie compresseur | ❌ Valeur aberrante (~592°C, utiliser R117) |
| R91 | Position EEV1 | ❌ Retourne 0 |
| R93 | Vitesse ventilateur UE | ❌ Retourne 0 |
| 5029 | Canaux actifs | ❌ Retourne 0 |
| 6021 | État circuit frigo | ❌ Retourne 0 |
| 20063 | État filtres | ❌ Retourne 0 |
| 30026 | Nb zones configurées | ❌ Retourne 0 |
| 31100-31104 | Écriture consignes thermostats | ❌ KO tous modèles (écriture impossible) |

---

## Ressources

| Ressource | Lien |
|-----------|------|
| Projet TOUG (djtef) | https://github.com/djtef/toug |
| Forum HACF | https://forum.hacf.fr/t/aldes-t-one-air-aquaair/42974 |

---

*Documentation TOUG_RBUV*
