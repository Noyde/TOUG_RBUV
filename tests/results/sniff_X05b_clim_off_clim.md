# Test X05b - Sniffing Clim Confort → Off → Clim Confort

**Date** : 2025-01-13 ~11:35
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Action effectuée

1. État initial : Clim Confort (On)
2. Appui : **Off**
3. Attente 2-3 sec
4. Appui : **Clim**

## Trames capturées

### État 1 : Clim Confort On (offset 0x0000)

```
00000020: 000c 0000 0003 000a 7ffe 7ffe 0028 00ff  .............(..
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 32-33 | 00 0c | ??? (Chauffage) |
| 34-35 | 00 00 | Vacances = Off |
| 36-37 | 00 03 | On/Off = **On** |
| 38-39 | 00 0a | Type mode = **Clim** |

### État 2 : Off (offset 0x0172)

```
00000190: 00f0 000c 0000 0002 000a 7ffe 7ffe 0028  ...............(
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 32-33 | 00 0c | ??? (Chauffage - inchangé!) |
| 34-35 | 00 00 | Vacances = Off |
| 36-37 | 00 02 | On/Off = **Off** |
| 38-39 | 00 0a | Type mode = Clim (inchangé) |

### État 3 : Clim Confort On (offset 0x024E)

```
00000270: 000c 0000 0003 000a 7ffe 7ffe 0028 00ff  .............(..
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 32-33 | 00 0c | ??? (Chauffage - toujours!) |
| 34-35 | 00 00 | Vacances = Off |
| 36-37 | 00 03 | On/Off = **On** |
| 38-39 | 00 0a | Type mode = **Clim** |

## Analyse

### ⭐ DÉCOUVERTE MAJEURE

L'offset **32-33 reste FIXE à 0x000C** même en mode Clim !

Le **vrai type mode** est à l'offset **38-39** :
- 0x000C = Chauffage
- 0x000A = Clim

### Résumé des transitions

| Transition | Offset 32-33 | Offset 36-37 | Offset 38-39 |
|------------|--------------|--------------|--------------|
| Clim On → Off | inchangé (0x000C) | 0x0003 → **0x0002** | inchangé (0x000A) |
| Off → Clim On | inchangé (0x000C) | 0x0002 → **0x0003** | inchangé (0x000A) |

### Hypothèse sur offset 32-33

Possibilités :
1. Mode par défaut / fallback
2. Dernier mode "chauffage" mémorisé
3. Champ non utilisé / legacy

## Résultat

- [x] ✅ PASS - Séquence Clim→Off→Clim capturée
- [x] ✅ Confirmé : On/Off à offset 36-37
- [x] ✅ Confirmé : Type mode réel à offset **38-39**
- [x] ⚠️ Offset 32-33 reste fixe à 0x000C

## Structure corrigée

| Offset | Description | Valeurs |
|--------|-------------|---------|
| 32-33 | ??? (toujours 0x000C) | À investiguer |
| 34-35 | Vacances | 0x0000=Off |
| 36-37 | On/Off | 0x0002=Off, 0x0003=On |
| **38-39** | **Type mode** | 0x000C=Chauffage, 0x000A=Clim |
