# Test X07 - Sniffing Chauffage Confort → Clim Confort → Clim Boost

**Date** : 2025-01-13 ~11:50
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Actions effectuées

1. État initial : Chauffage Confort
2. Action 1 : Passer en **Clim**
3. Action 2 : Passer en **Boost**

## Trames capturées

### État 1 : Chauffage Confort (offset 0x0000)

```
00000010: f67a 0000 0000 0000 0000 0384 0017 00f0  .z..............
00000020: 000c 0000 0003 000c 7ffe 7ffe 0028 00ff  .............(..
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 18-19 | 00 00 | Niveau = Confort |
| 20-21 | 00 00 | (padding) |
| 38-39 | 00 0c | Type = Chauffage |

### État 2 : Clim Confort (offset 0x0128)

```
00000140: 0000 0384 0017 00f0 000c 0000 0003 000a  ................
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 18-19 | 00 00 | Niveau = Confort |
| 38-39 | 00 0a | Type = **Clim** |

### État 3 : Clim Boost (offset 0x0206)

```
00000210: 7370 1804 a9ae f67a 0000 5678 0000 0000  sp.....z..Vx....
00000220: 0384 0017 00f0 000c 0000 0003 000a 7ffe  ................
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 18-19 | 00 00 | ??? |
| **20-21** | **56 78** | ⭐ **Boost** |
| 38-39 | 00 0a | Type = Clim |

## Analyse

### ⚠️ DÉCOUVERTE IMPORTANTE

La valeur Boost **0x5678** apparaît à l'offset **20-21**, pas 18-19 !

Comparaison avec Eco (X03) :
- Eco : offset 18-19 = 0x00C8
- Boost : offset 20-21 = 0x5678

### Hypothèse

Le champ Niveau pourrait être structuré différemment :
- Offset 18-19 : Niveau principal (Confort=0x0000, Eco=0x00C8)
- Offset 20-21 : Niveau secondaire / Boost (0x5678)

Ou bien le Boost utilise un champ séparé.

### Transitions observées

| Transition | Champ modifié | Valeur |
|------------|---------------|--------|
| Chauffage → Clim | Offset 38-39 | 0x000C → 0x000A |
| Confort → Boost | Offset 20-21 | 0x0000 → 0x5678 |

## Résultat

- [x] ✅ PASS - Boost capturé
- [x] ⚠️ CORRECTION - Boost à offset **20-21**, pas 18-19
- [x] ✅ Valeur 0x5678 = Boost confirmée

## Impact sur la documentation

La structure Niveau doit être clarifiée :
- Offset 18-19 : Eco (0x00C8) ou Confort (0x0000)
- Offset 20-21 : Boost (0x5678) ou 0x0000
