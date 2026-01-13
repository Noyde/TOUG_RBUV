# Aide-mémoire Sniffing 0x17

## Commandes rapides

```bash
# Configurer port (une fois)
stty -F /dev/ttyUSB0 19200 cs8 parenb -parodd -cstopb raw -echo

# Capture 10 secondes
timeout 10 cat /dev/ttyUSB0 > /tmp/sniff_XXX.bin && xxd /tmp/sniff_XXX.bin
```

## Tests modes PAC (X01-X10)

| ID | Action | Offset | Valeur attendue |
|----|--------|--------|-----------------|
| X01 | Chauffage → **Off** | 34-35 | `00 02` |
| X02 | Off → **Chauffage** | 34-35 | `00 03` |
| X03 | Confort → **Eco** | 18-19 | `00 C8` |
| X04 | Eco → **Confort** | 18-19 | `00 00` |
| X05 | Chauffage → **Clim** | 36-37 | `00 0A` |
| X06 | Clim → **Chauffage** | 36-37 | `00 0C` |
| X07 | Clim → **Boost** | 18-19 | `56 78` |
| X08 | **Vacances On** | 32-33 | `12 34` |
| X09 | **Vacances Off** | 32-33 | `00 00` |
| X10 | Cycle sous-codes | 2-3 | `00 01` → `00 41` → `00 81` → `00 C1` |

## Structure trame (74 bytes)

```
Offset  Description
------  -----------
00      Adresse (0x01)
01      Fonction (0x17)
02-03   Sous-code (cycle 01/41/81/C1)
04-05   Longueur (0x0040)
06-09   Constantes
10-11   Signature "sp" (0x7370)
12-13   Version (0x1804)
14-17   ?
18-19   ★ NIVEAU (00=Confort, C8=Eco, 5678=Boost)
20-31   ?
32-33   ★ VACANCES (00=Off, 1234=On)
34-35   ★ ON/OFF (02=Off, 03=On)
36-37   ★ TYPE (0C=Chauffage, 0A=Clim)
38-69   ?
70-71   ?
72-73   CRC16
```

## Fichiers résultats

Nommer les fichiers : `sniff_X01_chauffage_off.md`, `sniff_X02_off_chauffage.md`, etc.
