# Tests X19-X20 - Sniffing Date/Heure

**Date** : 2025-01-13 ~15:30
**Testeur** : Noyde
**Matériel** : Pi 2B + Waveshare RS485 (FT232RL)

## Configuration

- Télécommande : Débranchée de la PAC, connectée directement au Waveshare
- Port : /dev/ttyUSB0
- Baudrate : 19200, 8E1

## Tests effectués

### X19 - Capture baseline (sans modification)

**Heure affichée** : Vendredi 13 janvier 2031, 14h07

Extrait trame :
```
0117 0081 0040 0057 001f 7370 1804 c60c f67a 0000 0000 0000 0000 0384 0017 00f0
000c 0000 0003 000c 7ffe 7ffe 0028 00ff 01a4 7ffe 0000 7ffe 7ffe 0000 7ffe 7ffe
```

### X20 - Changement heure (+1h)

**Action** : Changer l'heure de 14h07 → 15h07

**Avant modification** (compteur c66d-c671) :
```
0117 0081 0040 0057 001f 7370 1804 c671 f67a 0000 0000 0000 0000 0384 0017 00f0
000c 0000 0003 000c 7ffe 7ffe 0028 00ff 01a4 7ffe 0000 7ffe 7ffe 0000 7ffe 7ffe
```

**Après modification** (compteur d450+) :
```
0117 00c1 003c 0057 001f 7370 1804 d450 f67a 0000 0000 0000 0000 0384 0017 00f0
000c 0000 0003 000c 7ffe 7ffe 0028 00ff 01a4 7ffe 0000 7ffe 7ffe 0000 7ffe 7ffe
```

## Résultat

### ❌ La date/heure N'EST PAS transmise dans la trame 0x17

| Élément | Avant | Après | Changement |
|---------|-------|-------|------------|
| Données (18-71) | identique | identique | ❌ Aucun |
| Compteur (14-15) | c671 | d450 | ✅ Normal (temps écoulé) |

## Conclusion

La **date/heure n'est pas encodée** dans les trames 0x17 envoyées par la télécommande.

### Hypothèses

1. **Stockage local** : La télécommande stocke l'heure localement pour l'affichage uniquement
2. **Synchronisation inverse** : La PAC envoie l'heure à la télécommande (dans les réponses 0x17 80xx)
3. **Horloges indépendantes** : Chaque appareil maintient sa propre horloge

### Implications

- Les tests X21-X23 (changement date, année, format) ne sont **pas pertinents**
- Pour synchroniser l'heure de la PAC, il faudrait analyser les **réponses** (Z01-Z05)
- Les registres R16/R17 (date/heure via USB) restent non fonctionnels sur RBUV

## Résultats tests

- [x] X19 - Capture baseline : ✅ Données stables
- [x] X20 - Changement heure : ❌ Pas de changement dans la trame
- [ ] X21-X23 : Non pertinents (date/heure non transmise)

## Note

L'année affichée (2031) suggère que l'horloge de la télécommande n'est pas synchronisée avec la PAC, confirmant l'hypothèse d'horloges indépendantes.
