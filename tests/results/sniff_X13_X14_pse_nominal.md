# Tests X13/X14 - Sniffing PSE Nominal (Mode Service)

**Date** : 2025-01-13 ~14:00
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1
- **Mode** : Installateur/Service (mot de passe requis)

## Actions effectuées

1. État initial : Mode service, PSE = 23 Pa
2. Modification : PSE nominal 23 → 24 Pa

## Résultats

### PSE Nominal (Offset 28-29)

Le PSE nominal est encodé à l'offset **28-29** en big-endian :

| PSE (Pa) | Hex | Capture |
|----------|-----|---------|
| 23 | 0x0017 | ✅ Confirmé (avant) |
| 24 | 0x0018 | ✅ Confirmé (après) |

## Trames capturées

### Avant modification (PSE = 23 Pa)

```
00000010: f67a 0000 0000 0000 3412 0384 0017 00f0  .z......4.......
00000020: 000c 0000 0003 000b 7ffe 7ffe 0028 00ff  .............(..
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 24-25 | 34 12 | Flag mode service |
| 26-27 | 03 84 | Débit nominal (900 m³/h) |
| 28-29 | **00 17** | PSE nominal (**23 Pa**) |
| 38-39 | 00 0b | Mode service (11) |

### Après modification (PSE = 24 Pa)

```
00000140: 3412 0384 0018 00f0 000c 0000 0003 000b  4...............
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 24-25 | 34 12 | Flag mode service |
| 26-27 | 03 84 | Débit nominal (900 m³/h) |
| 28-29 | **00 18** | PSE nominal (**24 Pa**) |

## Résultats

- [x] ✅ X13/X14 PASS - PSE nominal à offset **28-29**
- [x] ✅ Encodage big-endian confirmé
- [x] ✅ Valeur en Pascal (unité brute)

## Structure trame mise à jour

| Offset | Description | Valeurs |
|--------|-------------|---------|
| 24-25 | Flag mode service | 0x0000=Normal, 0x3412=Service |
| 26-27 | Débit nominal | m³/h (ex: 0x0384=900) |
| **28-29** | **PSE nominal** | Pa (ex: 0x0017=23, 0x0018=24) |
| 38-39 | Type mode étendu | 0x000A=Clim, 0x000B=Service, 0x000C=Chauffage |

## Prochaines étapes

- [ ] X15/X16 : Débit mini (offset à trouver)
- [ ] X17/X18 : PSE mini (offset à trouver)
