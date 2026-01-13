# Récapitulatif Tests Sniffing X01-X10

**Date** : 2025-01-13
**Testeur** : Noyde

## Tests complétés

| ID | Action | Offset | Valeur | Résultat |
|----|--------|--------|--------|----------|
| X01 | Chauffage → Off | 36-37 | 0x0002 | ✅ |
| X02 | Off → Chauffage | 36-37 | 0x0003 | ✅ |
| X03 | Confort → Eco | 18-19 | 0x00C8 | ✅ |
| X04 | Eco → Confort | 18-19 | 0x0000 | ✅ |
| X05 | Chauffage → Clim | **38-39** | 0x000A | ✅ |
| X06 | Clim → Chauffage | **38-39** | 0x000C | ✅ |
| X07 | Confort → Boost | **20-21** | 0x5678 | ✅ |
| X08 | Vacances On | 34-35 | 0x1234 | ✅ |
| X09 | Vacances Off | 34-35 | 0x0000 | ✅ |
| X10 | Cycle sous-codes | 2-3 | 01→41→81→C1 | ✅ |

## Structure trame 0x17 CORRIGÉE

```
Offset  Bytes  Description              Valeurs
------  -----  -----------------------  ---------------------------
0-1     2      Adresse + Fonction       01 17
2-3     2      Sous-code (cycle)        0001 → 0041 → 0081 → 00C1
4-5     2      Longueur données         0040 (64) ou 003C (60)
6-7     2      ???                      00 57
8-9     2      ???                      00 1f
10-11   2      Signature                73 70 ("sp")
12-13   2      ???                      18 04
14-15   2      Compteur (incrémente)    Variable
16-17   2      ???                      f6 7a
18-19   2      Niveau Eco               0x0000=Confort, 0x00C8=Eco
20-21   2      Niveau Boost             0x0000=Normal, 0x5678=Boost
22-25   4      Padding                  00 00 00 00
26-27   2      Débit nominal            03 84 (900 m³/h)
28-29   2      PSE nominal              00 17 (23 Pa)
30-31   2      ???                      00 f0
32-33   2      ??? (toujours 0x000C)    00 0c
34-35   2      Vacances                 0x0000=Off, 0x1234=On
36-37   2      On/Off                   0x0002=Off, 0x0003=On
38-39   2      Type mode                0x000C=Chauffage, 0x000A=Clim
40-71   32     Données (7ffe padding)   ...
72-73   2      CRC16 Modbus             Variable
```

## Corrections par rapport à la doc initiale

| Champ | Doc initiale | Réalité |
|-------|--------------|---------|
| Type mode | Offset 32-33 | **Offset 38-39** |
| Boost | Offset 18-19 | **Offset 20-21** |
| Offset 32-33 | Type mode | **Toujours 0x000C** (usage inconnu) |

## Découvertes importantes

### 1. Structure Niveau (2 champs séparés)

| Mode | Offset 18-19 | Offset 20-21 |
|------|--------------|--------------|
| Confort | 0x0000 | 0x0000 |
| Eco | 0x00C8 | 0x0000 |
| Boost | 0x0000 | 0x5678 |

### 2. Comportement Vacances

- Active le flag 0x1234 à l'offset 34-35
- **Force le mode Chauffage** si on était en Clim
- Restaure le mode précédent à la désactivation
- Le nombre de jours n'est PAS dans la trame

### 3. Offset 32-33 mystérieux

- Reste **toujours à 0x000C** (Chauffage)
- Même en mode Clim !
- Usage exact inconnu

### 4. Cycle sous-codes

```
0x0001 → 0x0041 → 0x0081 → 0x00C1 → (répète)
```

Intervalle ~1.5 sec entre chaque trame.

## Impact sur le code ESP32

Le fichier `esphome/components/aldes_tone/aldes_tone.h` doit être corrigé :

```cpp
// AVANT (incorrect)
trame[32] = (vacances >> 8) & 0xFF;  // Vacances
trame[34] = (onoff >> 8) & 0xFF;     // On/Off
trame[36] = (type_mode >> 8) & 0xFF; // Type

// APRÈS (correct)
trame[34] = (vacances >> 8) & 0xFF;  // Vacances
trame[36] = (onoff >> 8) & 0xFF;     // On/Off
trame[38] = (type_mode >> 8) & 0xFF; // Type
```

Et pour Boost :
```cpp
// Boost à offset 20-21, pas 18-19
trame[20] = (boost >> 8) & 0xFF;
trame[21] = boost & 0xFF;
```

## Prochaines étapes

1. ✅ Tous les tests modes PAC complétés
2. ⬜ Corriger `aldes_tone.h` avec les nouveaux offsets
3. ⬜ Tester l'envoi de trames avec ESP32
4. ⬜ Valider les offsets ventilation (26-31)
