# Test X02 - Sniffing Off → Chauffage Confort

**Date** : 2025-01-13 ~11:00
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Action effectuée

1. État initial : Off
2. Appui sur bouton : **Chauffage**

## Commande

```bash
stty -F /dev/ttyUSB0 19200 cs8 parenb -parodd -cstopb raw -echo
timeout 10 cat /dev/ttyUSB0 > /tmp/sniff_X02.bin
xxd /tmp/sniff_X02.bin
```

## Trames capturées (hex)

### Trames avant appui (état Off) - offset 0x0000 à 0x0170

```
00000000: 0117 00c1 003c 0057 001f 7370 1804 a674  .....<.W..sp...t
00000010: f67a 0000 0000 0000 0000 0384 0017 00f0  .z..............
00000020: 000c 0000 0002 000c 7ffe 7ffe 0028 00ff  .............(..
...
00000140: 0000 0384 0017 00f0 000c 0000 0002 000c  ................
```

### Trame après appui (état On) - offset 0x0172

```
00000170: 13ad 0117 0001 0040 0057 001f 7370 1804  .......@.W..sp..
00000180: a67b f67a 0000 0000 0000 0000 0384 0017  .{.z............
00000190: 00f0 000c 0000 0003 000c 7ffe 7ffe 0028  ...............(
000001a0: 00ff 01a4 7ffe 0000 7ffe 7ffe 0000 7ffe  ................
```

## Analyse

### Changement observé

| Offset | Avant (Off) | Après (On) | Description |
|--------|-------------|------------|-------------|
| 36-37 | 00 02 | **00 03** | ⭐ On/Off |

### Structure trame confirmée

| Offset | Hex | Valeur | Description |
|--------|-----|--------|-------------|
| 0 | 01 | 1 | Adresse Modbus |
| 1 | 17 | 0x17 | Fonction Read/Write Multiple |
| 2-3 | 00 01 | Cycle | Sous-code (01→41→81→C1) |
| 4-5 | 00 40 | 64 | Longueur données |
| 10-11 | 73 70 | "sp" | Signature |
| 14-15 | a6 7b | Variable | Compteur (incrémente) |
| 18-19 | 00 00 | 0 | **Niveau** = Confort |
| 26-27 | 03 84 | 900 | **Débit nominal** (m³/h) |
| 28-29 | 00 17 | 23 | **PSE nominal** (Pa) |
| 32-33 | 00 0c | 12 | **Type mode** = Chauffage |
| 34-35 | 00 00 | 0 | **Vacances** = Off |
| **36-37** | **00 03** | **3** | ⭐ **On/Off = ON** |
| 38-39 | 00 0c | 12 | Type mode (copie) |

### Cycle sous-codes observé

```
0x00C1 (trame 1)
0x0001 (trame 2) ← Changement On/Off ici
0x0041 (trame 3)
0x0081 (trame 4)
0x00C1 (trame 5)
0x0001 (trame 6)
0x0041 (trame 7)
```

### Compteur incrémental (offset 14-15)

```
a674 → a676 → a677 → a678 → a67a → a67b → a67d
```

## Résultat

- [x] ✅ PASS - Off→On fonctionne
- [x] ✅ Offset 36-37 confirmé pour On/Off
- [x] ✅ Valeur 0x0003 = On confirmée

## Correspondance avec X01

| Test | Action | Offset | Valeur |
|------|--------|--------|--------|
| X01 | On → Off | 36-37 | 0x0003 → 0x0002 |
| X02 | Off → On | 36-37 | 0x0002 → 0x0003 |

✅ **Cohérent** : On/Off bien à l'offset 36-37
