# Test X09 - Sniffing Vacances Off

**Date** : 2025-01-13 ~12:10
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Action effectuée

1. État initial : Vacances (Chauffage forcé)
2. Action : Désactiver **Vacances**
3. Résultat : Retour au mode précédent (Clim Confort)

## Trames capturées

### Avant (Vacances On) - offset 0x0000

```
00000020: 000c 1234 0003 000c 7ffe 7ffe 0028 00ff  ...4.........(..
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 32-33 | 00 0c | ??? |
| 34-35 | 12 34 | Vacances = On |
| 36-37 | 00 03 | On/Off = On |
| 38-39 | 00 0c | Type = Chauffage (forcé) |

### Après (Vacances Off) - offset 0x0128

```
00000140: 0000 0384 0017 00f0 000c 0000 0003 000a  ................
```

| Offset | Valeur | Description |
|--------|--------|-------------|
| 32-33 | 00 0c | ??? |
| 34-35 | **00 00** | ⭐ **Vacances = Off** |
| 36-37 | 00 03 | On/Off = On |
| 38-39 | **00 0a** | Type = **Clim** (restauré!) |

## Analyse

### Changements observés

| Offset | Avant | Après | Description |
|--------|-------|-------|-------------|
| 34-35 | 12 34 | **00 00** | ⭐ Vacances Off |
| 38-39 | 00 0c | **00 0a** | Chauffage → Clim |

### ⭐ DÉCOUVERTE

La PAC **restaure le mode précédent** (Clim) quand on désactive Vacances.

Le mode Vacances mémorise donc l'état précédent pour le restaurer.

### Valeurs confirmées

| Valeur | Description |
|--------|-------------|
| 0x0000 | Vacances Off |
| 0x1234 | Vacances On |

## Résultat

- [x] ✅ PASS - Vacances Off capturé
- [x] ✅ Offset 34-35 confirmé (bidirectionnel)
- [x] ✅ Valeur 0x0000 = Vacances Off confirmée
- [x] ⭐ Découverte : Mode précédent restauré automatiquement

## Récapitulatif Vacances

| Test | Transition | Offset 34-35 | Offset 38-39 |
|------|------------|--------------|--------------|
| X08 | Clim → Vacances | 0x0000 → 0x1234 | 0x000A → 0x000C |
| X09 | Vacances → Off | 0x1234 → 0x0000 | 0x000C → 0x000A |
