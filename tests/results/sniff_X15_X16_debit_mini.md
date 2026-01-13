# Tests X15/X16 - Sniffing Débit Mini 1 Bouche (Mode Service)

**Date** : 2025-01-13 ~14:30
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1
- **Mode** : Installateur/Service (mot de passe requis)

## Actions effectuées

1. État initial : Mode service, Débit 1 bouche = 240 m³/h
2. Modification : 240 → 220 m³/h

## Résultats

### Débit Mini 1 Bouche (Offset 30-31)

Le débit mini par bouche est encodé à l'offset **30-31** en big-endian :

| Débit (m³/h) | Hex | Capture |
|--------------|-----|---------|
| 240 | 0x00F0 | ✅ Confirmé (avant) |
| 220 | 0x00DC | ✅ Confirmé (après) |

## Trames capturées

### Avant modification (Débit 1 bouche = 240)

```
00000010: f67a 0000 0000 0000 3412 0384 0017 00f0  .z......4.......
00000020: 000c 0000 0003 000b 7ffe 7ffe 0028 00ff  .............(..
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 24-25 | 34 12 | Flag mode service |
| 26-27 | 03 84 | Débit nominal (900 m³/h) |
| 28-29 | 00 17 | PSE nominal (23 Pa) |
| 30-31 | **00 F0** | Débit 1 bouche (**240 m³/h**) |

### Après modification (Débit 1 bouche = 220)

```
000001d0: 0000 0000 3412 0384 0017 00dc 000c 0000  ....4...........
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 26-27 | 03 84 | Débit nominal (900 m³/h) |
| 28-29 | 00 17 | PSE nominal (23 Pa) |
| 30-31 | **00 DC** | Débit 1 bouche (**220 m³/h**) |

## Résultats

- [x] ✅ X15/X16 PASS - Débit mini 1 bouche à offset **30-31**
- [x] ✅ Encodage big-endian confirmé
- [x] ✅ Valeur en m³/h (unité brute)

## Structure trame mise à jour

| Offset | Description | Valeurs |
|--------|-------------|---------|
| 24-25 | Flag mode service | 0x0000=Normal, 0x3412=Service |
| 26-27 | Débit nominal | m³/h (ex: 0x0384=900) |
| 28-29 | PSE nominal | Pa (ex: 0x0017=23) |
| **30-31** | **Débit 1 bouche** | m³/h (ex: 0x00F0=240, 0x00DC=220) |

## Correspondance registres Modbus

| Offset trame | Registre USB | Description |
|--------------|--------------|-------------|
| 26-27 | R250 | Débit nominal |
| 28-29 | R247 | PSE débit nominal |
| **30-31** | **R249** | Débit 1 bouche |

## Prochaines étapes

- [ ] X17/X18 : PSE mini (offset à trouver)
