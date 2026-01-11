# Rapport de test TOUG_RBUV

**Date**: 2026-01-11 17:55:32
**Port**: /dev/ttyACM1
**Baudrate**: 1200

## System

| Registre | Description | Valeur | Statut |
|----------|-------------|--------|--------|
| R1 | Version Firmware | 3019 | ✅ |
| R3 | Durée ON | 0 min | ✅ |
| R9 | Mode PAC | 4 (Chauffage) | ✅ |

## Consignes

| Registre | Description | Valeur | Statut |
|----------|-------------|--------|--------|
| R20 | Consigne Zone 1 | 21.00 °C | ✅ |
| R21 | Consigne Zone 1 bis | 21.00 °C | ✅ |
| R22 | Consigne Zone 2 | 19.00 °C | ✅ |
| R23 | Consigne Zone 3 | 21.00 °C | ✅ |
| R24 | Consigne Zone 4 | 20.00 °C | ✅ |
| R25 | Consigne Zone 5 | 20.00 °C | ✅ |

## Temperatures

| Registre | Description | Valeur | Statut |
|----------|-------------|--------|--------|
| R36 | Température Zone 1 | 21.00 °C | ✅ |
| R37 | Température Zone 1 bis | 21.00 °C | ✅ |
| R38 | Température Zone 2 | 19.68 °C | ✅ |
| R39 | Température Zone 3 | 21.93 °C | ✅ |
| R40 | Température Zone 4 | 20.75 °C | ✅ |
| R41 | Température Zone 5 | 20.37 °C | ✅ |

## Ventilation

| Registre | Description | Valeur | Statut |
|----------|-------------|--------|--------|
| R60 | Consigne Ventilateur | 0 rpm | ✅ |
| R61 | Vitesse Ventilateur | 0 rpm | ✅ |
| R106 | Niveau Ventilation UE | 0 | ✅ |
| R125 | Heures Ventilateur | 25500 h | ✅ |

## Compresseur

| Registre | Description | Valeur | Statut |
|----------|-------------|--------|--------|
| R65 | Consigne Fréquence | 0.0 Hz | ✅ |
| R66 | Fréquence Compresseur | 0.0 Hz | ✅ |
| R127 | Heures Compresseur | 12600 h | ✅ |

## Pac

| Registre | Description | Valeur | Statut |
|----------|-------------|--------|--------|
| R111 | T° Air Repris UI | 20.03 °C | ✅ |
| R112 | T° Extérieure | 4.53 °C | ✅ |
| R114 | T° Échangeur UI | 18.18 °C | ✅ |
| R115 | T° Échangeur UE | 6.40 °C | ✅ |
| R117 | T° Sortie Compresseur | 31.57 °C | ✅ |

## Eev

| Registre | Description | Valeur | Statut |
|----------|-------------|--------|--------|
| R104 | EEV1 | 110 Pls | ✅ |
| R105 | EEV2 | 0 Pls | ✅ |

## Debits

| Registre | Description | Valeur | Statut |
|----------|-------------|--------|--------|
| R247 | PSE Débit Nominal | 23 Pa | ✅ |
| R248 | PSE Débit Mini | 12 Pa | ✅ |
| R249 | Débit 1 Bouche | 240 m³/h | ✅ |
| R250 | Débit Nominal | 900 m³/h | ✅ |
| R251 | Pression Statique Ext | 10 Pa | ✅ |

---

**Résumé**: 34/34 registres OK
