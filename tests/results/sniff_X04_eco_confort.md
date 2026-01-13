# Test X04 - Sniffing Eco → Confort

**Date** : 2025-01-13 ~11:20
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Action effectuée

1. État initial : Chauffage Eco
2. Action : Revenir en mode **Confort**

## Commande

```bash
stty -F /dev/ttyUSB0 19200 cs8 parenb -parodd -cstopb raw -echo
timeout 10 cat /dev/ttyUSB0 > /tmp/sniff_X04.bin
xxd /tmp/sniff_X04.bin
```

## Trames capturées (hex)

### Trames avant (Eco) - offset 0x0000 à 0x0120

```
00000000: 0117 0081 0040 0057 001f 7370 1804 a780  .....@.W..sp....
00000010: f67a 00c8 0000 0000 0000 0384 0017 00f0  .z..............
```

Offset 18-19 dans la trame = `00 c8` (Eco)

### Trame après (Confort) - offset 0x0128

```
00000120: 7ffe 0000 0000 9f7d 0117 0081 0040 0057  .......}.....@.W
00000130: 001f 7370 1804 a786 f67a 0000 0000 0000  ..sp.....z......
00000140: 0000 0384 0017 00f0 000c 0000 0003 000c  ................
```

Offset 18-19 dans la trame = `00 00` (Confort)

## Analyse

### Changement observé

| Offset | Avant (Eco) | Après (Confort) | Description |
|--------|-------------|-----------------|-------------|
| 18-19 | 00 C8 | **00 00** | ⭐ Niveau |

### Valeurs confirmées

- 0x00C8 = Eco (200 en décimal)
- 0x0000 = Confort (0 en décimal)

### Autres champs (inchangés)

| Offset | Valeur | Description |
|--------|--------|-------------|
| 32-33 | 00 0c | Type mode = Chauffage |
| 34-35 | 00 00 | Vacances = Off |
| 36-37 | 00 03 | On/Off = On |

## Résultat

- [x] ✅ PASS - Eco→Confort fonctionne
- [x] ✅ Offset 18-19 confirmé pour Niveau (bidirectionnel)
- [x] ✅ Valeur 0x0000 = Confort confirmée
