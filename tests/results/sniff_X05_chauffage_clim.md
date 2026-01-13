# Test X05 - Sniffing Chauffage → Clim

**Date** : 2025-01-13 ~11:25
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Action effectuée

1. État initial : Chauffage Confort
2. Action : Passer en mode **Clim Confort**

## Commande

```bash
stty -F /dev/ttyUSB0 19200 cs8 parenb -parodd -cstopb raw -echo
timeout 10 cat /dev/ttyUSB0 > /tmp/sniff_X05.bin
xxd /tmp/sniff_X05.bin
```

## Trames capturées (hex)

### Trames avant (Chauffage) - offset 0x0000

```
00000000: 0117 0001 0040 0057 001f 7370 1804 a7dc  .....@.W..sp....
00000010: f67a 0000 0000 0000 0000 0384 0017 00f0  .z..............
00000020: 000c 0000 0003 000c 7ffe 7ffe 0028 00ff  .............(..
```

- Offset 32-33 = `00 0c` (Chauffage)
- Offset 38-39 = `00 0c` (Chauffage)

### Trame après (Clim) - offset 0x0172

```
00000170: b85a 0117 0041 0040 0057 001f 7370 1804  .Z...A.@.W..sp..
00000180: a7e4 f67a 0000 0000 0000 0000 0384 0017  ...z............
00000190: 00f0 000c 0000 0003 000a 7ffe 7ffe 0028  ...............(
```

- Offset 32-33 = `00 0c` (Chauffage - **INCHANGÉ**)
- Offset 38-39 = `00 0a` (Clim - **CHANGÉ**)

## Analyse

### ⚠️ DÉCOUVERTE IMPORTANTE

Le changement de type mode n'est PAS à l'offset 32-33 comme attendu, mais à l'offset **38-39** !

| Offset | Avant | Après | Description |
|--------|-------|-------|-------------|
| 32-33 | 00 0c | 00 0c | Type mode (inchangé!) |
| 38-39 | 00 0c | **00 0a** | ⭐ Type mode **réel** |

### Hypothèse

- **Offset 32-33** : Type mode actuel/précédent (lecture ?)
- **Offset 38-39** : Type mode demandé/commande (écriture ?)

Ou bien les deux doivent être identiques pour une commande valide.

### Valeurs confirmées

- 0x000C = Chauffage (12 en décimal)
- 0x000A = Clim (10 en décimal)

### Autres champs

| Offset | Valeur | Description |
|--------|--------|-------------|
| 18-19 | 00 00 | Niveau = Confort |
| 34-35 | 00 00 | Vacances = Off |
| 36-37 | 00 03 | On/Off = On |

## Résultat

- [x] ✅ PASS - Chauffage→Clim capturé
- [x] ⚠️ CORRECTION - Type mode à l'offset **38-39**, pas 32-33
- [x] ✅ Valeur 0x000A = Clim confirmée

## Impact sur la documentation

La structure trame doit être corrigée :
- Offset 32-33 : Usage à clarifier (type actuel ?)
- Offset 38-39 : Type mode commande (Chauffage/Clim)
