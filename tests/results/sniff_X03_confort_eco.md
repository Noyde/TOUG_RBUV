# Test X03 - Sniffing Confort → Eco

**Date** : 2025-01-13 ~11:15
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Action effectuée

1. État initial : Chauffage Confort (On)
2. Action : Passer en mode **Eco**

## Commande

```bash
stty -F /dev/ttyUSB0 19200 cs8 parenb -parodd -cstopb raw -echo
timeout 10 cat /dev/ttyUSB0 > /tmp/sniff_X03.bin
xxd /tmp/sniff_X03.bin
```

## Trames capturées (hex)

### Trames avant (Confort) - offset 0x0000 à 0x0170

```
00000000: 0117 0081 0040 0057 001f 7370 1804 a72c  .....@.W..sp...,
00000010: f67a 0000 0000 0000 0000 0384 0017 00f0  .z..............
00000020: 000c 0000 0003 000c 7ffe 7ffe 0028 00ff  .............(..
```

Offset 18-19 dans la trame = `00 00` (Confort)

### Trame après (Eco) - offset 0x0172

```
00000170: da3e 0117 00c1 003c 0057 001f 7370 1804  .>.....<.W..sp..
00000180: a733 f67a 00c8 0000 0000 0000 0384 0017  .3.z............
00000190: 00f0 000c 0000 0003 000c 7ffe 7ffe 0028  ...............(
```

Offset 18-19 dans la trame = `00 c8` (Eco)

## Analyse

### Changement observé

| Offset | Avant (Confort) | Après (Eco) | Description |
|--------|-----------------|-------------|-------------|
| 18-19 | 00 00 | **00 C8** | ⭐ Niveau |

### Valeurs confirmées

- 0x0000 = Confort (200 en décimal = 0)
- 0x00C8 = Eco (200 en décimal = 200)

### Autres champs (inchangés)

| Offset | Valeur | Description |
|--------|--------|-------------|
| 32-33 | 00 0c | Type mode = Chauffage |
| 34-35 | 00 00 | Vacances = Off |
| 36-37 | 00 03 | On/Off = On |

## Résultat

- [x] ✅ PASS - Confort→Eco fonctionne
- [x] ✅ Offset 18-19 confirmé pour Niveau
- [x] ✅ Valeur 0x00C8 = Eco confirmée
