# Rapport de recherche - Registres Modbus non documentés

**Date**: 2025-01-12
**Port**: /dev/ttyACM1
**Baudrate**: 1200
**Objectif**: Explorer les registres au-delà de la documentation TOUG

## Contexte

Recherche web sur le protocole Modbus Aldes T.One, puis tests de lecture pour découvrir des registres non documentés.

### Sources consultées (hors TOUG/HACF)

- [guix77/esphome-aldes-tone](https://github.com/guix77/esphome-aldes-tone) - Projet ESPHome alternatif
- [Jeedom - Pilotage Aldes T One](https://community.jeedom.com/t/pilotage-aldes-t-one/93229) - Reverse engineering communautaire
- [ManualsLib - SAT Modbus RTU](https://www.manualslib.fr/manual/33379/Aldes-Sat-Modbus-Rtu.html) - Documentation Aldes officielle (autre produit)

---

## Tests effectués

### Test 1: Adresse esclave

| Adresse | Résultat |
|---------|----------|
| 1 | ✅ Répond |
| 2 | ❌ No communication |

**Conclusion**: Adresse esclave = 1 confirmée

### Test 2: Registres guix77 (mapping alternatif)

| Registre | guix77 | Valeur RBUV | Observation |
|----------|--------|-------------|-------------|
| R120 (0x0078) | Temp principale | 16.00°C | Dynamique (parfois 0) |
| R122 (0x007A) | Mode | 164 | Stable, pas un mode |
| R130 (0x0082) | Filtre | 0 | OK |
| R150 (0x0096) | Consigne K1a | 384 | Pas une température |

**Conclusion**: Les registres existent mais ont un sens différent sur RBUV 2018

### Test 3: Magic number Aldes (R0-R3)

| Registre | Valeur | Attendu |
|----------|--------|---------|
| R0 | 0 | 19533 |
| R1 | 3019 | 20051 |
| R2 | 566 | - |
| R3 | 36 | - |

**Conclusion**: Pas de magic number Aldes. R1 = version firmware (déjà connu)

### Test 4: Compteur temps R131

```
 0s: R131 = 35079  -> 9h44m39s
 5s: R131 = 35084 (+5) -> 9h44m44s
10s: R131 = 35089 (+5) -> 9h44m49s
...
55s: R131 = 35134 (+5) -> 9h45m34s
```

**Conclusion**: R131 = compteur temps en secondes (probablement temps compresseur actif)

---

## Scan complet R0-R500

**Résultat**: 203 registres non-nuls trouvés

### Registres système

| Registre | Valeur | Description | Statut |
|----------|--------|-------------|--------|
| R1 | 3019 | Version Firmware | ✅ Connu |
| R6 | 44093 | ? | ⬜ Inconnu |
| R7 | 174 | ? | ⬜ Inconnu |
| R8 | 19 | ? | ⬜ Inconnu |
| R9 | 4 | Mode PAC (Chauffage) | ✅ Connu |
| R14 | 1 | ? | ⬜ Inconnu |

### Consignes thermostats (R20-R25)

| Registre | Valeur | Zone | Statut |
|----------|--------|------|--------|
| R20 | 19.00°C | Zone 1 | ✅ Connu |
| R21 | 19.00°C | Zone 1 bis | ✅ Connu |
| R22 | 17.00°C | Zone 2 | ✅ Connu |
| R23 | 19.00°C | Zone 3 | ✅ Connu |
| R24 | 18.00°C | Zone 4 | ✅ Connu |
| R25 | 18.00°C | Zone 5 | ✅ Connu |

### Températures zones (R36-R41)

| Registre | Valeur | Zone | Statut |
|----------|--------|------|--------|
| R36 | 18.81°C | Zone 1 | ✅ Connu |
| R37 | 18.81°C | Zone 1 bis | ✅ Connu |
| R38 | 17.93°C | Zone 2 | ✅ Connu |
| R39 | 18.93°C | Zone 3 | ✅ Connu |
| R40 | 17.93°C | Zone 4 | ✅ Connu |
| R41 | 17.81°C | Zone 5 | ✅ Connu |

### Compteurs 32-bits (R44-R55) - NOUVEAU

Pattern: registre pair = valeur haute, impair = 243

| Registres | Valeur | Hypothèse |
|-----------|--------|-----------|
| R44-R45 | 59271 / 243 | Compteur Zone 1 ? |
| R46-R47 | 59271 / 243 | Compteur Zone 1bis ? |
| R48-R49 | 57859 / 243 | Compteur Zone 2 ? |
| R50-R51 | 57827 / 243 | Compteur Zone 3 ? |
| R52-R53 | 57854 / 243 | Compteur Zone 4 ? |
| R54-R55 | 57824 / 243 | Compteur Zone 5 ? |

### Registres ventilation/régulation (R60-R85)

| Registre | Valeur | Description | Statut |
|----------|--------|-------------|--------|
| R63 | 30 | ? | ⬜ Inconnu |
| R67 | 16 | ? | ⬜ Inconnu |
| R69 | 32768 (0x8000) | Flag ? | ⬜ Inconnu |
| R70 | 20.00°C | **Consigne générale ?** | 🔍 À valider |
| R71 | 17.45°C | T° référence ? | 🔍 À valider |
| R76 | 32767 (0x7FFF) | Max value / flag | ⬜ Inconnu |

### Températures PAC (R104-R117)

| Registre | Valeur | Description | Statut |
|----------|--------|-------------|--------|
| R104 | 1.10°C | EEV1 / Évaporateur | ✅ Connu |
| R107 | 0.17°C | ? | ⬜ Inconnu |
| R108 | 0.16°C | ? | ⬜ Inconnu |
| R110 | 2.55°C | ? | ⬜ Inconnu |
| R111 | 18.51°C | T° Air Repris UI | ✅ Connu |
| R112 | 11.29°C | T° Extérieure | ✅ Connu |
| R113 | 17.45°C | ? | 🔍 À valider |
| R114 | 17.45°C | T° Échangeur UI | ✅ Connu |
| R115 | 9.52°C | T° Échangeur UE | ✅ Connu |
| R117 | 27.03°C | T° Sortie Compresseur | ✅ Connu |

### Compteurs temps (R131-R138)

| Registre | Valeur | Description | Statut |
|----------|--------|-------------|--------|
| R131 | 44069 | **Compteur secondes** (12h14m29s) | ✅ Validé |
| R132 | 3 | ? | ⬜ Inconnu |
| R133 | 4.94°C | ? | ⬜ Inconnu |
| R134 | 14.79°C | ? | ⬜ Inconnu |
| R135 | 24.11°C | ? | ⬜ Inconnu |
| R136 | 44069 | Miroir R131 | ✅ Validé |
| R137 | 3 | ? | ⬜ Inconnu |
| R138 | 3.05°C | ? | ⬜ Inconnu |

### Registres R141-R170 - NOUVEAU

| Registre | Valeur | Hex | Hypothèse |
|----------|--------|-----|-----------|
| R141 | 7044 | 0x1B84 | Compteur ? |
| R142-R148 | 5-6 / 5937-5938 | - | Paires compteur ? |
| R150 | 384 | 0x0180 | Dynamique |
| R151 | 2739 | 0x0AB3 | Dynamique |
| R160 | 103 | 0x0067 | Compteur lent |
| R162-R167 | 65478-65504 | 0xFFC6-0xFFE0 | Signed: -58 à -32 |
| R170-R175 | 175-1590 | - | Températures ? |

### Registres R194-R210 - NOUVEAU

| Registre | Valeur | Description | Statut |
|----------|--------|-------------|--------|
| R194-R199 | 176-1591 | Miroir R170-R175 ? | ⬜ Inconnu |
| R203 | 52171 | ? (valeur variable) | ⬜ Inconnu |
| R204 | 23.84°C | Température interne | 🔍 À valider |
| R207 | 65436 | Signed: -100 | ⬜ Inconnu |
| R210 | 20.00°C | **= R70 = R101** | 🔍 À valider |

### Registres R317-R393 - NOUVEAU (jamais documenté)

| Registre | Valeur | Hypothèse |
|----------|--------|-----------|
| R317-R322 | 2-5 | États/flags par zone ? |
| R325-R330 | 91-279 | Stats zones ? |
| R341 | 170 | ? |
| R342 | 920 | ? |
| R343 | 120 | ? |
| R346 | 17218 (0x4342) | ASCII "CB" ? |
| R349 | 900 | = R250 (débit nominal) |
| R351 | 100 | ? |
| R352 | 130 | ? |
| **R362** | **16.00°C** | **Seuil bas ?** |
| **R363** | **24.00°C** | **Seuil haut ?** |
| **R364** | **22.00°C** | **Consigne clim ?** |
| **R365** | **31.00°C** | **Seuil alarme ?** |
| R374 | 2.00°C | Hystérésis ? |
| R375-R381 | Divers | ? |
| R390-R393 | 1-12 | ? |

---

## Découvertes clés

### 1. R120 est DYNAMIQUE

Observé à 16.00°C dans certains scans, absent (=0) dans d'autres.
Hypothèse: valeur active qui dépend de l'état de la PAC.

### 2. Triple consigne 20°C

```
R70  = 2000 = 20.0°C
R101 = 2000 = 20.0°C
R210 = 2000 = 20.0°C
```

Ces 3 registres ont la même valeur. Consigne générale dupliquée ?

### 3. R362 = 16.0°C = ancien R120 ?

R362 a la même valeur que R120 avait. Peut-être le registre de configuration dont R120 est la copie active.

### 4. Seuils température (R362-R365)

| Registre | Valeur | Hypothèse |
|----------|--------|-----------|
| R362 | 16.0°C | Seuil bas (antigel ?) |
| R363 | 24.0°C | Seuil haut été |
| R364 | 22.0°C | Consigne clim |
| R365 | 31.0°C | Alarme surchauffe |

### 5. Zone R300+ existe

169 registres trouvés dans la zone R0-R300, mais aussi des registres dans R317-R393.
Cette zone n'est documentée nulle part.

---

## À valider (nécessite console PAC)

| Question | Registre | Comment valider |
|----------|----------|-----------------|
| Consigne affichée = 20°C ? | R70/R101/R210 | Lire écran PAC |
| R362-R365 = seuils ? | R362-R365 | Chercher dans menus PAC |
| R120 change avec mode ? | R120 | Basculer Eco ↔ Confort |
| R204 = quelle température ? | R204 | Comparer avec écran |

---

## Résumé

| Catégorie | Nombre |
|-----------|--------|
| Registres trouvés | 203 |
| Déjà documentés (TOUG) | ~40 |
| **Nouveaux découverts** | **~163** |
| Validés cette session | 3 (R131, R136, adresse) |
| À valider sur console | ~10 |

---

**Note**: Mode PAC pendant les tests = Chauffage Eco (R9=4)
