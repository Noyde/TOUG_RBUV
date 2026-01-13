# Test X01 - Sniffing Chauffage Confort → Off

**Date** : 2025-01-13 ~10:30
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Action effectuée

1. État initial : Chauffage Confort (On)
2. Appui sur bouton : **Off**

## Commande

```bash
stty -F /dev/ttyUSB0 19200 cs8 parenb -parodd -cstopb raw -echo
timeout 10 cat /dev/ttyUSB0 > /tmp/sniff_X01.bin
xxd /tmp/sniff_X01.bin
```

## Trames capturées (hex)

### Trame avant Off (état On) - offset 0x0000

```
00000000: 0117 0081 0040 0057 001f 7370 1804 a33b  .....@.W..sp...;
00000010: f67a 0000 0000 0000 0000 0384 0017 00f0  .z..............
00000020: 000c 0000 0003 000c 7ffe 7ffe 0028 00ff  .............(..
00000030: 01a4 7ffe 0000 7ffe 7ffe 0000 7ffe 7ffe  ................
00000040: 7ffe 7ffe 0000 0000 17a4                 ..........
```

### Trame après Off - offset 0x0140

```
00000140: 0117 0081 0040 0057 001f 7370 1804 a340  .....@.W..sp...@
00000150: f67a 0000 0000 0000 0000 0384 0017 00f0  .z..............
00000160: 000c 0000 0002 000c 7ffe 7ffe 0028 00ff  .............(..
00000170: 01a4 7ffe 0000 7ffe 7ffe 0000 7ffe 7ffe  ................
```

## Analyse

### Structure trame corrigée (74 bytes)

| Offset | Hex (On) | Hex (Off) | Valeur | Description |
|--------|----------|-----------|--------|-------------|
| 0 | 01 | 01 | 1 | Adresse Modbus |
| 1 | 17 | 17 | 0x17 | Fonction Read/Write Multiple |
| 2-3 | 00 81 | 00 81 | Cycle | Sous-code (81→C1→01→41→81) |
| 4-5 | 00 40 | 00 40 | 64 | Longueur données |
| 6-7 | 00 57 | 00 57 | 87 | Constante |
| 8-9 | 00 1f | 00 1f | 31 | Constante |
| 10-11 | 73 70 | 73 70 | "sp" | Signature |
| 12-13 | 18 04 | 18 04 | 0x1804 | Version protocole |
| 14-15 | a3 3b | a3 40 | Variable | Compteur (incrémente) |
| 16-17 | f6 7a | f6 7a | ? | Constante ? |
| 18-19 | 00 00 | 00 00 | 0 | **Niveau** (0=Confort) |
| 20-25 | 00... | 00... | 0 | Padding ? |
| 26-27 | 03 84 | 03 84 | 900 | **Débit nominal** (m³/h) |
| 28-29 | 00 17 | 00 17 | 23 | **PSE nominal** (Pa) |
| 30-31 | 00 f0 | 00 f0 | 240 | ? (débit mini ?) |
| 32-33 | 00 0c | 00 0c | 12 | **Type mode** (0x0C=Chauffage) |
| 34-35 | 00 00 | 00 00 | 0 | **Vacances** (0=Off) |
| **36-37** | **00 03** | **00 02** | **On/Off** | ⭐ **0x03=On, 0x02=Off** |
| 38-39 | 00 0c | 00 0c | 12 | Type mode (dupliqué ?) |
| 40-41 | 7f fe | 7f fe | 0x7FFE | Consigne Z1 (pas de changement) |
| 42-43 | 7f fe | 7f fe | 0x7FFE | Consigne Z2 |
| 44-45 | 00 28 | 00 28 | 40 | ? |
| 46-47 | 00 ff | 00 ff | 255 | ? |
| 48-49 | 01 a4 | 01 a4 | 420 | ? |
| 50-69 | 7ffe... | 7ffe... | Pattern | Consignes zones (0x7FFE) |
| 70-71 | 00 00 | 00 00 | 0 | ? |
| 72-73 | 17 a4 | 7a 23 | CRC | CRC16 Modbus |

### Vérification On/Off

- **Offset réel** : 36-37 (pas 34-35 comme documenté !)
- Valeur On (avant) : `0x0003`
- Valeur Off (après) : `0x0002`
- **Correspondance** : ✅ OUI

### Cycle sous-codes observé

```
0x0081 → 0x00C1 → 0x0001 → 0x0041 → 0x0081 (répète)
```
✅ Confirmé

### Compteur incrémental (offset 14-15)

```
a33b → a33c → a33e → a33f → a340 → a342 → a343
```
Incrémente à chaque trame (parfois +1, parfois +2)

## Résultat

- [x] ✅ PASS - On/Off fonctionne
- [x] ⚠️ CORRECTION - Offset réel = 36-37, pas 34-35

## Découvertes importantes

1. **Offset On/Off corrigé** : 36-37 (pas 34-35)
2. **Offset Type mode** : 32-33 (pas 36-37)
3. **Offset Vacances** : 34-35 (pas 32-33)
4. **Débit nominal confirmé** : offset 26-27 = 0x0384 = 900
5. **PSE nominal confirmé** : offset 28-29 = 0x0017 = 23
6. **Pattern 0x7FFE** : confirmé pour consignes non modifiées

## Structure corrigée

| Offset | Description | Valeurs |
|--------|-------------|---------|
| 18-19 | Niveau | 0x0000=Confort, 0x00C8=Eco, 0x5678=Boost |
| 26-27 | Débit nominal | En m³/h (ex: 0x0384=900) |
| 28-29 | PSE nominal | En Pa (ex: 0x0017=23) |
| 32-33 | Type mode | 0x000C=Chauffage, 0x000A=Clim |
| 34-35 | Vacances | 0x0000=Off, 0x1234=On |
| **36-37** | **On/Off** | **0x0002=Off, 0x0003=On** |
