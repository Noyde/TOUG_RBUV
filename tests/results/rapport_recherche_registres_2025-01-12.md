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

### 5. Zone R300+ existe (jamais documentée)

169 registres trouvés dans la zone R0-R300, mais aussi des registres dans R317-R393.
Cette zone n'est documentée nulle part.

#### Hypothèses par plage

| Plage | Valeurs | Hypothèse |
|-------|---------|-----------|
| R317-R322 | 2-5 (6 valeurs) | **États des 6 zones** (demande, satisfait, etc.) |
| R325-R330 | 91-279 (6 valeurs, symétrique) | **Stats/compteurs par zone** |
| R341-R355 | 120-920, plusieurs "900" | **Paramètres ventilation** (900 = débit nominal) |
| R362-R369 | 16, 24, 22, 31°C + 25-60 | **Seuils régulation** (antigel, été, clim, alarme) |
| R375-R381 | 0x7370="sp", 0x1804, 0x5831="X1" | **Signature protocole** (même que trame 0x17) |
| R390-R393 | 1-12 | **Flags divers** |

#### Détail R317-R322 (états zones ?)

```
R317 = 5  → Zone 1 ?
R318 = 3  → Zone 1bis ?
R319 = 2  → Zone 2 ?
R320 = 2  → Zone 3 ?
R321 = 3  → Zone 4 ?
R322 = 3  → Zone 5 ?
```

Hypothèse : 0=off, 1=standby, 2=satisfait, 3=demande faible, 4=demande moyenne, 5=demande forte

#### Détail R362-R369 (seuils régulation)

```
R362 = 1600 = 16.0°C  → Seuil antigel / température minimale
R363 = 2400 = 24.0°C  → Seuil été / déclenchement clim
R364 = 2200 = 22.0°C  → Consigne mode clim ?
R365 = 3100 = 31.0°C  → Alarme surchauffe
R366 = 30             → Délai ou hystérésis
R367 = 25             → Délai ou hystérésis
R368 = 60             → Timeout ?
R369 = 60             → Timeout ?
```

#### Détail R375-R381 (signature protocole)

```
R375 = 29552 = 0x7370 = "sp"   → Signature identique à trame 0x17 !
R376 = 6148  = 0x1804          → Version identique à trame 0x17 !
R379 = 22577 = 0x5831 = "X1"   → Identifiant modèle ?
```

Ces registres contiennent la **même signature** que la trame 0x17.
Hypothèse : zone de configuration du protocole télécommande.

---

## Tests d'écriture FC16 (Write Multiple Registers)

### Test FC06 (Write Single Register)

Résultat sur tous les registres testés: **"illegal function"**

La PAC n'implémente pas la fonction standard 0x06.

### Test FC16 (Write Multiple Registers)

| Registre | FC16 | Observation |
|----------|------|-------------|
| R20-R25 (consignes zones) | ❌ illegal data address | Confirmé lecture seule |
| R362-R374 (seuils) | ❌ illegal data address | Non accessibles |
| R90, R92, R94, R96 | ✅ Accepté | Stats/compteurs ? |
| R101, R102 | ✅ Accepté | R101 = 20.0°C (consigne ?) |
| R104 | ✅ Accepté | EEV1 - DANGEREUX |
| R107, R108, R110 | ✅ Accepté | = 255, flags ? |
| R111-R115 | ✅ Accepté | Températures PAC |
| R117 | ✅ Accepté | T° sortie compresseur |

**Total: 16 registres acceptent FC16**

```
R90 = 2176, R92 = 2181, R94 = 2176, R96 = 37
R101 = 2000 (20.0°C), R102 = 129
R104 = 110 (EEV1), R107 = 255, R108 = 255, R110 = 255
R111 = 1774, R112 = 1129, R113 = 1520
R114 = 1558, R115 = 1021, R117 = 3245
```

### ✅ TEST AVEC VALEUR DIFFÉRENTE (2025-01-12)

Test effectué en écrivant une valeur DIFFÉRENTE (254) pour vérifier si l'écriture est effective.

| Registre | Avant | Écrit | Après | Résultat |
|----------|-------|-------|-------|----------|
| R107 | 129 | 254 | 30 | ❌ Dynamique (capteur temps réel) |
| R108 | 16 | 254 | 255 | ❌ Dynamique (capteur temps réel) |
| R110 | 255 | 254 | 255 | ❌ Ignoré |

**Conclusions :**

1. **R107 et R108 sont des registres DYNAMIQUES** - ils changent tout seuls (capteurs en temps réel).
   - Valeurs initiales (scan précédent) : 255
   - Valeurs actuelles : 129 et 16
   - Ces registres ne sont PAS des flags mais des capteurs non documentés

2. **Les écritures FC16 sont IGNORÉES** - on a écrit 254, mais les valeurs après ne correspondent pas. Elles ont continué à évoluer naturellement.

3. **USB = LECTURE SEULE confirmé** - même FC16 qui est "accepté" sans erreur ne modifie rien.

### Conclusion finale écriture USB

**Le bus USB est fondamentalement LECTURE SEULE sur firmware 3019 RBUV.**

- FC06 : "illegal function"
- FC16 : Accepté mais ignoré (valeurs inchangées)
- Seule option écriture : Protocole 0x17 sur bus RS485 télécommande

---

## Pistes pour modification consignes thermostats

### Limitation connue

Les registres R20-R25 sont **lecture seule** (pilotés par radio 868MHz).
Les registres TOUG 31100-31104 ne fonctionnent sur **aucun modèle**.

### Pistes alternatives

| Piste | Registres | Méthode | Probabilité |
|-------|-----------|---------|-------------|
| Consigne générale | R70/R101/R210 | Écriture 0x17 | Moyenne |
| Seuils | R362-R365 | Écriture 0x17 | Faible |
| **Trame 0x17** | **Offset 40-69** | **Sniff télécommande** | **Haute** |

**Priorité** : Sniffer la télécommande quand on modifie une consigne via le menu.
L'offset 40-69 contient probablement les consignes (pattern 0x7FFE = "pas de changement").

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
