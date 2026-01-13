# Test X07b - Sniffing Clim Boost → Clim Confort

**Date** : 2025-01-13 ~11:55
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Action effectuée

1. État initial : Clim Boost
2. Action : Revenir en **Confort**

## Trames capturées

### Avant (Boost) - offset 0x0000

```
00000010: f67a 0000 5678 0000 0000 0384 0017 00f0  .z..Vx..........
```

- Offset 18-19 = `00 00`
- Offset 20-21 = `56 78` (Boost)

### Après (Confort) - offset 0x0128

```
00000130: 001f 7370 1804 aa54 f67a 0000 0000 0000  ..sp...T.z......
```

- Offset 18-19 = `00 00`
- Offset 20-21 = `00 00` (Confort)

## Analyse

### Changement observé

| Offset | Avant (Boost) | Après (Confort) | Description |
|--------|---------------|-----------------|-------------|
| 18-19 | 00 00 | 00 00 | Inchangé |
| 20-21 | 56 78 | **00 00** | ⭐ Boost → Confort |

### Confirmation structure Niveau

| Mode | Offset 18-19 | Offset 20-21 |
|------|--------------|--------------|
| Confort | 0x0000 | 0x0000 |
| Eco | 0x00C8 | 0x0000 |
| Boost | 0x0000 | 0x5678 |

## Résultat

- [x] ✅ PASS - Boost→Confort fonctionne
- [x] ✅ Offset 20-21 confirmé pour Boost (bidirectionnel)
- [x] ✅ Structure Niveau clarifiée

## Récapitulatif complet Niveau

| Test | Transition | Offset | Changement |
|------|------------|--------|------------|
| X03 | Confort → Eco | 18-19 | 0x0000 → 0x00C8 |
| X04 | Eco → Confort | 18-19 | 0x00C8 → 0x0000 |
| X07 | Confort → Boost | 20-21 | 0x0000 → 0x5678 |
| X07b | Boost → Confort | 20-21 | 0x5678 → 0x0000 |
