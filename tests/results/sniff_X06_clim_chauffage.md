# Test X06 - Sniffing Clim → Chauffage

**Date** : 2025-01-13 ~11:40
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Action effectuée

1. État initial : Clim Confort (On)
2. Action : Passer en mode **Chauffage**

## Trames capturées

### Avant (Clim) - offset 0x0000

```
00000020: 000c 0000 0003 000a 7ffe 7ffe 0028 00ff  .............(..
```

- Offset 32-33 = `00 0c` (fixe)
- Offset 38-39 = `00 0a` (Clim)

### Après (Chauffage) - offset 0x0172

```
00000190: 00f0 000c 0000 0003 000c 7ffe 7ffe 0028  ...............(
```

- Offset 32-33 = `00 0c` (fixe, inchangé)
- Offset 38-39 = `00 0c` (Chauffage)

## Analyse

### Changement observé

| Offset | Avant (Clim) | Après (Chauffage) | Description |
|--------|--------------|-------------------|-------------|
| 32-33 | 00 0c | 00 0c | Fixe (inchangé) |
| 38-39 | 00 0a | **00 0c** | ⭐ Type mode |

### Valeurs confirmées

- 0x000A = Clim (10 en décimal)
- 0x000C = Chauffage (12 en décimal)

## Résultat

- [x] ✅ PASS - Clim→Chauffage fonctionne
- [x] ✅ Offset 38-39 confirmé pour Type mode (bidirectionnel)
- [x] ✅ Offset 32-33 reste fixe à 0x000C

## Récapitulatif Type mode

| Test | Transition | Offset 38-39 |
|------|------------|--------------|
| X05 | Chauffage → Clim | 0x000C → 0x000A |
| X05b | Clim → Off → Clim | reste 0x000A |
| X06 | Clim → Chauffage | 0x000A → 0x000C |
