# Test X01 - Sniffing Chauffage Confort → Off

**Date** : YYYY-MM-DD HH:MM
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Action effectuée

1. État initial : Chauffage Confort
2. Appui sur bouton : **Off**

## Commande

```bash
stty -F /dev/ttyUSB0 19200 cs8 parenb -parodd -cstopb raw -echo
timeout 10 cat /dev/ttyUSB0 > /tmp/sniff_X01.bin
xxd /tmp/sniff_X01.bin
```

## Trame capturée (hex)

```
[COLLER LA SORTIE XXD ICI]
```

## Analyse

### Trame complète (74 bytes attendus)

| Offset | Hex | Valeur | Description |
|--------|-----|--------|-------------|
| 0 | | | Adresse Modbus |
| 1 | | | Fonction (0x17) |
| 2-3 | | | Sous-code |
| ... | | | |
| 18-19 | | | Niveau |
| 32-33 | | | Vacances |
| 34-35 | | | **On/Off (attendu: 0x0002)** |
| 36-37 | | | Type mode |
| 72-73 | | | CRC16 |

### Vérification offset 34-35

- Valeur capturée : `0x____`
- Valeur attendue : `0x0002` (Off)
- Correspondance : ⬜ OUI / ⬜ NON

## Résultat

- [ ] ✅ PASS - Offset 34-35 = 0x0002
- [ ] ❌ FAIL - Valeur différente
- [ ] ⚠️ PARTIAL - Trame incomplète ou autre

## Notes

[Observations, anomalies, différences avec la doc...]
