# Tests X17/X18 - Sniffing PSE Mini (Mode Service)

**Date** : 2025-01-13 ~15:00
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1
- **Mode** : Installateur/Service (mot de passe requis)

## Actions effectuées

1. État initial : Mode service, PSE mini = 12 Pa
2. Modification : 12 → 11 Pa

## Résultats

### PSE Mini (Offset 32-33)

Le PSE mini est encodé à l'offset **32-33** en big-endian :

| PSE mini (Pa) | Hex | Capture |
|---------------|-----|---------|
| 12 | 0x000C | ✅ Confirmé (avant) |
| 11 | 0x000B | ✅ Confirmé (après) |

## ⭐ DÉCOUVERTE IMPORTANTE

L'offset **32-33** n'est **PAS** "Type mode" comme supposé initialement !

### Pourquoi l'erreur ?

| Valeur | Signification supposée | Signification réelle |
|--------|------------------------|----------------------|
| 0x000C | Chauffage | **12 Pa** (PSE mini) |
| 0x000A | Clim | **10 Pa** (si PSE mini = 10) |

La valeur 0x000C (12) à l'offset 32-33 correspondait par **coïncidence** au code Chauffage. En réalité, c'est la valeur du PSE mini en Pa !

### Conséquence

Le "Type mode" est **uniquement** à l'offset **38-39**, pas de copie à 32-33.

## Trames capturées

### Avant modification (PSE mini = 12 Pa)

```
00000010: f67a 0000 0000 0000 3412 0384 0017 00f0  .z......4.......
00000020: 000c 0000 0003 000b 7ffe 7ffe 0028 00ff  .............(..
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 26-27 | 03 84 | Débit nominal (900 m³/h) |
| 28-29 | 00 17 | PSE nominal (23 Pa) |
| 30-31 | 00 F0 | Débit 1 bouche (240 m³/h) |
| 32-33 | **00 0C** | PSE mini (**12 Pa**) |
| 38-39 | 00 0B | Type mode = Service |

### Après modification (PSE mini = 11 Pa)

```
00000140: 3412 0384 0017 00f0 000b 0000 0003 000b  4...............
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 26-27 | 03 84 | Débit nominal (900 m³/h) |
| 28-29 | 00 17 | PSE nominal (23 Pa) |
| 30-31 | 00 F0 | Débit 1 bouche (240 m³/h) |
| 32-33 | **00 0B** | PSE mini (**11 Pa**) |
| 38-39 | 00 0B | Type mode = Service |

## Résultats

- [x] ✅ X17/X18 PASS - PSE mini à offset **32-33**
- [x] ✅ Encodage big-endian confirmé
- [x] ✅ Valeur en Pa (unité brute)
- [x] ⭐ Correction : offset 32-33 ≠ Type mode

## Structure trame CORRIGÉE

| Offset | Description | Valeurs |
|--------|-------------|---------|
| 26-27 | Débit nominal | m³/h |
| 28-29 | PSE nominal | Pa |
| 30-31 | Débit 1 bouche | m³/h |
| **32-33** | **PSE mini** | Pa (ex: 0x000C=12, 0x000B=11) |
| 34-35 | Vacances | 0x0000=Off, 0x1234=On |
| 36-37 | On/Off | 0x0002=Off, 0x0003=On |
| **38-39** | **Type mode** | 0x000A=Clim, 0x000B=Service, 0x000C=Chauffage |

## Correspondance registres Modbus

| Offset trame | Registre USB | Description |
|--------------|--------------|-------------|
| 26-27 | R250 | Débit nominal |
| 28-29 | R247 | PSE débit nominal |
| 30-31 | R249 | Débit 1 bouche |
| **32-33** | **R248** | PSE débit mini |

## Tests ventilation COMPLÉTÉS ✅

Tous les offsets ventilation sont maintenant confirmés :
- X11/X12 : Débit nominal → offset 26-27
- X13/X14 : PSE nominal → offset 28-29
- X15/X16 : Débit 1 bouche → offset 30-31
- X17/X18 : PSE mini → offset 32-33
