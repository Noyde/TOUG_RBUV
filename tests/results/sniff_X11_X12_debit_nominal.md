# Tests X11/X12 - Sniffing Débit Nominal (Mode Service)

**Date** : 2025-01-13 ~13:00
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1
- **Mode** : Installateur/Service (mot de passe requis)

## Actions effectuées

1. Entrée en mode installateur (mot de passe)
2. Modification débit nominal : 900 → 880 → 840 → 900

## Découvertes majeures

### 1. Flag Mode Installateur (Offset 24-25)

Quand on entre en mode service, l'offset 24-25 passe de `00 00` à `34 12` :

| Mode | Offset 24-25 | Description |
|------|--------------|-------------|
| Normal | 00 00 | Mode utilisateur |
| Service | **34 12** | Mode installateur |

### 2. Mode Service (Offset 38-39)

En mode service, l'offset 38-39 change :

| Mode | Offset 38-39 | Description |
|------|--------------|-------------|
| Chauffage | 00 0c | Mode normal (12) |
| Clim | 00 0a | Mode normal (10) |
| **Service** | **00 0b** | Mode installateur (11) |

### 3. Débit Nominal (Offset 26-27)

Le débit nominal est encodé à l'offset **26-27** en big-endian :

| Débit (m³/h) | Hex | Capture |
|--------------|-----|---------|
| 900 | 0x0384 | ✅ Confirmé |
| 880 | 0x0370 | ✅ Confirmé |
| 840 | 0x0348 | ✅ Confirmé |

**Note** : Le pas de modification est de 20 m³/h (pas 10).

## Trames capturées

### État initial (880 m³/h)

```
00000010: f67a 0000 0000 0000 3412 0370 0017 00f0  .z......4..p....
00000020: 000c 0000 0003 000b 7ffe 7ffe 0028 00ff  .............(..
```

- Offset 24-25 : `34 12` (mode service)
- Offset 26-27 : `03 70` (880 m³/h)
- Offset 28-29 : `00 17` (23 Pa - PSE)
- Offset 38-39 : `00 0b` (mode service)

### Après 880 → 840

```
00000260: f67a 0000 0000 0000 3412 0348 0017 00f0  .z......4..H....
```

- Offset 26-27 : `03 48` (840 m³/h) ✅

### Après 840 → 900

```
00000390: 3412 0384 0017 00f0 000c 0000 0003 000b  4...............
```

- Offset 26-27 : `03 84` (900 m³/h) ✅

## Résultats

- [x] ✅ X11/X12 PASS - Débit nominal à offset **26-27**
- [x] ✅ Découverte : Flag mode service à offset **24-25** = 0x3412
- [x] ✅ Découverte : Mode service à offset **38-39** = 0x000B
- [x] ✅ Mot de passe géré côté télécommande (pas transmis)

## Structure trame mise à jour

| Offset | Description | Valeurs |
|--------|-------------|---------|
| 24-25 | **Flag mode service** | 0x0000=Normal, 0x3412=Service |
| **26-27** | **Débit nominal** | m³/h (ex: 0x0384=900) |
| 28-29 | PSE nominal | Pa (ex: 0x0017=23) |
| 38-39 | Type mode étendu | 0x000A=Clim, 0x000B=Service, 0x000C=Chauffage |

## Prochaines étapes

- [ ] X13/X14 : Valider PSE nominal (offset 28-29)
- [ ] X15-X18 : Débit/PSE mini (offsets à trouver)
