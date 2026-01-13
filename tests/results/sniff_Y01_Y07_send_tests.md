# Tests envoi trame 0x17 - Y01-Y07

**Date** : 2025-01-13
**Matériel** : Raspberry Pi 2B + Waveshare USB-RS485 (FT232RL)
**Bus** : RS485 télécommande (19200 bauds, 8E1)
**Méthode** : Envoi direct Python, vérification R9 via Modbus

## Contexte

Suite à la validation du protocole 0x17 par sniffing (X01-X20), tests d'envoi réel de trames vers la PAC pour confirmer le contrôle bidirectionnel.

## Configuration matérielle

- Pi 2B connecté directement au bus RS485 de la PAC (télécommande débranchée)
- Port : `/dev/ttyUSB0`
- Paramètres : 19200 bauds, 8 bits, parité EVEN, 1 stop

## Résultats

| Test | Mode | Offset modifié | Valeur | R9 attendu | R9 obtenu | Statut |
|------|------|----------------|--------|------------|-----------|--------|
| Y01 | Off | 36-37 | 0x0002 | 5 | 5 | ✅ PASS |
| Y02 | Chauffage Confort | 36-37, 38-39 | 0x0003, 0x000C | 4 | 4 | ✅ PASS |
| Y03 | Chauffage Eco | 18-19 | 0x00C8 | 4 | 4 | ✅ PASS* |
| Y04 | Clim Confort | 38-39 | 0x000A | 2 | 2 | ✅ PASS |
| Y05 | Clim Boost | 20-21 | 0x5678 | 2 | 2 | ✅ PASS* |
| Y06 | Vacances On | 34-35 | 0x1234 | - | - | ✅ PASS** |
| Y07 | Retour Chauffage | 34-35 | 0x0000 | 4 | 4 | ✅ PASS |

\* Eco/Boost non distinguables via R9 (pas de registre dédié)
\** Vacances visible sur dashboard, R9 inchangé

## Trames de référence

### Y01 - Off
```
01 17 00 01 00 40 00 57 00 1f 73 70 18 04 00 01 f6 7a
00 00 00 00 00 00 00 00 03 84 00 17 00 f0 00 0c
00 00 00 02 00 0c 7f fe 7f fe 7f fe 7f fe 7f fe
7f fe 7f fe 7f fe 7f fe 7f fe 7f fe 7f fe 7f fe
7f fe 7f fe 00 00 [CRC]
```

Réponse PAC (133 bytes) :
```
01 17 80 0b cb 00 00 00 00 00 00 00 00 13 a9 00 ae ...
```

### Y04 - Clim Confort
Différence : offset 38-39 = 0x000A (au lieu de 0x000C)

### Y05 - Clim Boost
Différences :
- offset 20-21 = 0x5678 (Boost)
- offset 38-39 = 0x000A (Clim)

## Observations

1. **Réponse PAC** : Toujours ~133 bytes avec en-tête `01 17 80 xx`
2. **Délai** : Changement d'état quasi-instantané (<200ms)
3. **Lecture R9** : Nécessite flush buffer (écho convertisseur RS485)
4. **Eco/Boost** : Pas de registre Modbus pour distinguer, validation par sniffing uniquement

## Commande lecture R9

```python
import minimalmodbus
import time
i = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
i.serial.baudrate = 19200
i.serial.parity = 'E'
i.serial.timeout = 1
i.serial.reset_input_buffer()
time.sleep(0.1)
i.serial.reset_input_buffer()
print(f'R9 = {i.read_register(9)}')
```

## Conclusion

**Protocole 0x17 validé en écriture** : Le Pi 2B peut contrôler la PAC via RS485.

Prochaines étapes :
- Mettre à jour le composant ESPHome `aldes_tone.h` avec les offsets corrects
- Tester envoi depuis ESP32
- Documentation finale
