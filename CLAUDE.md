# Contexte projet TOUG_RBUV

## Résumé
Domotisation PAC Aldes T.One AIR RBUV (2018) via Home Assistant. Modèle : T.One AIR 04 (RBC04MX/RBUV04F), firmware 3019.

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
- Registres TOUG 31100-31104 = non implémentés sur modèle 2018

## Structure trame 0x17 (74 bytes)
- Offset 18-19: Niveau (0x0000=Confort, 0x00C8=Eco, 0x5678=Boost)
- Offset 32-33: Vacances (0x0000=Off, 0x1234=On)
- Offset 34-35: On/Off (0x0002=Off, 0x0003=On)
- Offset 36-37: Type (0x000C=Chauffage, 0x000A=Clim)
- Offset 72-73: CRC16 Modbus

## Mapping thermostats corrigé
| Registre | Zone |
|----------|------|
| 20 | Salon (K1a) |
| 21 | Cuisine (K1b) - même thermostat que 20 |
| 22 | Ch. Parentale |
| 23 | Bureau |
| 24 | Ch. Angèle |
| 25 | Ch. Marcus |

## Statut projet
- ✅ Lecture 34 registres via Pi Zero USB
- ✅ Protocole 0x17 documenté
- ⚠️ Composant ESPHome à revalider
- ⚠️ Projet BETA - utilisation à vos risques

## Ressources
- Repo: https://github.com/Noyde/TOUG_RBUV
- TOUG (djtef): https://github.com/djtef/toug
- Forum HACF: https://forum.hacf.fr/t/aldes-t-one-air-aquaair/42974
