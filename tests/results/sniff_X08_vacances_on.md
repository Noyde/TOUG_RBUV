# Test X08 - Sniffing Clim → Vacances (1 jour)

**Date** : 2025-01-13 ~12:05
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Action effectuée

1. État initial : Clim Confort
2. Action : Activer **Vacances** (1 jour)

## Trames capturées

### Avant (Clim Confort) - offset 0x0000

```
00000020: 000c 0000 0003 000a 7ffe 7ffe 0028 00ff  .............(..
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 32-33 | 00 0c | ??? |
| 34-35 | 00 00 | Vacances = Off |
| 36-37 | 00 03 | On/Off = On |
| 38-39 | 00 0a | Type = Clim |

### Après (Vacances) - offset 0x0172

```
00000190: 00f0 000c 1234 0003 000c 7ffe 7ffe 0028  .....4.........(
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 32-33 | 00 0c | ??? |
| 34-35 | **12 34** | ⭐ **Vacances = On** |
| 36-37 | 00 03 | On/Off = On |
| 38-39 | **00 0c** | Type = **Chauffage** (forcé!) |

## Analyse

### Changements observés

| Offset | Avant | Après | Description |
|--------|-------|-------|-------------|
| 34-35 | 00 00 | **12 34** | ⭐ Vacances On |
| 38-39 | 00 0a | **00 0c** | Clim → Chauffage |

### ⭐ DÉCOUVERTE

Le mode Vacances **force le passage en Chauffage** (offset 38-39 = 0x000C).

C'est logique : en vacances, on veut maintenir le chauffage au minimum pour éviter le gel, pas la climatisation.

### Valeur Vacances confirmée

- 0x0000 = Vacances Off
- 0x1234 = Vacances On

### Note sur le nombre de jours

Le nombre de jours (1 jour dans ce test) n'apparaît pas dans les offsets observés. Il est peut-être :
- Stocké ailleurs dans la trame (après offset 40)
- Géré différemment par la PAC

## Résultat

- [x] ✅ PASS - Vacances capturé
- [x] ✅ Offset 34-35 confirmé pour Vacances
- [x] ✅ Valeur 0x1234 = Vacances On confirmée
- [x] ⭐ Découverte : Vacances force le mode Chauffage
