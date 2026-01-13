# Tests TOUG_RBUV

Matrice de tests pour valider le fonctionnement sur PAC Aldes T.One RBUV (modèles 2018).

> **Objectif** : Comparer les registres documentés dans TOUG (djtef) avec ce qui fonctionne réellement sur le modèle RBUV.

---

## Prérequis

### Matériel

| Équipement | Usage | Port |
|------------|-------|------|
| Pi Zero 2 W | Lecture USB | /dev/ttyACM1 |
| Pi 2B + Waveshare RS485 | Sniffing télécommande | /dev/ttyUSB0 |
| ESP32 D1 Mini | Envoi trames 0x17 | GPIO16/17 |

### Conditions

- **Télécommande DÉBRANCHÉE** pour tests écriture (collision bus sinon)
- PAC sous tension et en fonctionnement normal
- Accès SSH aux Pi

### Dépendances Python

```bash
sudo apt install python3-serial
```

---

## Résumé des tests (2025-01-12)

| Groupe | Total | OK | KO | À faire | Notes |
|--------|-------|----|----|---------|-------|
| **Lecture USB** | | | | | |
| RBUV (34 registres) | 34 | 34 | 0 | 0 | ✅ Tous fonctionnent |
| TOUG System | 7 | 5 | 2 | 0 | R16/R17 non fonctionnels |
| TOUG Temperatures | 3 | 3 | 0 | 0 | R44 valeur aberrante |
| TOUG Ventilation | 4 | 4 | 0 | 0 | R91/R93 = 0 |
| TOUG Extended | 4 | 0 | 4 | 0 | ❌ Non implémentés |
| TOUG Consignes | 5 | 0 | 5 | 0 | ❌ Confirmé KO |
| **Exploration registres** | | | | | |
| Adresse esclave | 1 | 1 | 0 | 0 | ✅ Adresse 1 confirmée |
| Registres guix77 | 5 | 5 | 0 | 0 | ✅ Existent, sens différent |
| Compteurs temps | 2 | 2 | 0 | 0 | ✅ R131/R136 validés |
| Scan R0-R500 | 203 | 40 | 0 | 163 | 🔍 À identifier |
| Scan R1000-R1033 | 20 | 0 | 0 | 20 | 🔍 Zone calibration ? |
| **Écriture Modbus** | | | | | |
| USB (standard) | 8 | 0 | 8 | 0 | ✅ Échec attendu |
| USB FC16 | 9 | 0 | 9 | 0 | ✅ Accepté mais ignoré (USB read-only) |
| RS485 (standard) | 2 | 0 | 0 | 2 | ⬜ W03-W04 |
| **Protocole 0x17** | | | | | |
| Sniff modes PAC | 10 | 0 | 0 | 10 | ⬜ X01-X10 |
| Sniff ventilation | 8 | 0 | 0 | 8 | ⬜ X11-X18 |
| Sniff date/heure | 5 | 0 | 0 | 5 | ⬜ X19-X23 |
| Sniff consignes | 4 | 0 | 0 | 4 | ⬜ X24-X27 |
| Sniff analyse trame | 4 | 0 | 0 | 4 | ⬜ X28-X31 |
| Envoi modes PAC | 7 | 0 | 0 | 7 | ⬜ Y01-Y07 |
| Envoi ventilation | 6 | 0 | 0 | 6 | ⬜ Y08-Y13 |
| Envoi date/heure | 2 | 0 | 0 | 2 | ⬜ Y14-Y15 |
| Réponses PAC | 5 | 0 | 0 | 5 | ⬜ Z01-Z05 |

---

## 1. Registres lecture (USB 1200 bauds)

### 1.1 Système

| ID | Reg | Hex | Description | Diviseur | TOUG | Résultat | Date |
|----|-----|-----|-------------|----------|------|----------|------|
| S01 | 1 | 0x01 | Version firmware | 1 | ✅ | ✅ 3019 | 2025-01-10 |
| S02 | 3 | 0x03 | Durée ON (min) | 1 | ✅ | ✅ 36 min | 2025-01-10 |
| S03 | 9 | 0x09 | Mode PAC | 1 | ✅ | ✅ 4 (Chauffage) | 2025-01-10 |
| S04 | 14-15 | 0x0E | Panel ID (32-bit) | 1 | ✅ | ✅ 1, 0 | 2025-01-10 |
| S05 | 16 | 0x10 | Date encodée | 1 | ✅ | ❌ Non fonctionnel RBUV | 2025-01-11 |
| S06 | 17 | 0x11 | Heure encodée | 1 | ✅ | ❌ Non fonctionnel RBUV | 2025-01-11 |
| S07 | 51 | 0x33 | Protection compresseur | 1 | ✅ | ✅ 243 | 2025-01-10 |
| S08 | 90 | 0x5A | Code défaut UE | 1 | ✅ | ⚠️ 700 | 2025-01-10 |
| S09 | 131 | 0x83 | État dégivrage | 1 | ✅ | ⚠️ 11274 | 2025-01-10 |

**Note R16/R17** : Tests 2025-01-11 avec changements date/heure sur PAC → valeurs incohérentes et instables. La date/heure n'est probablement accessible que via le bus RS485 télécommande avec le protocole 0x17, pas via USB.

### 1.2 Consignes thermostats (lecture seule)

| ID | Reg | Hex | Zone | Diviseur | TOUG | Résultat | Date |
|----|-----|-----|------|----------|------|----------|------|
| C01 | 20 | 0x14 | Zone 1 (K1a) | ÷100 | ✅ | ✅ 21.00°C | 2025-01-10 |
| C02 | 21 | 0x15 | Zone 1 bis (K1b) | ÷100 | ✅ | ✅ 21.00°C | 2025-01-10 |
| C03 | 22 | 0x16 | Zone 2 | ÷100 | ✅ | ✅ 19.00°C | 2025-01-10 |
| C04 | 23 | 0x17 | Zone 3 | ÷100 | ✅ | ✅ 21.00°C | 2025-01-10 |
| C05 | 24 | 0x18 | Zone 4 | ÷100 | ✅ | ✅ 21.00°C | 2025-01-10 |
| C06 | 25 | 0x19 | Zone 5 | ÷100 | ✅ | ✅ 20.00°C | 2025-01-10 |

### 1.3 Températures zones

| ID | Reg | Hex | Zone | Diviseur | Signé | Résultat | Date |
|----|-----|-----|------|----------|-------|----------|------|
| T01 | 36 | 0x24 | Zone 1 | ÷100 | Oui | ✅ 21.06°C | 2025-01-10 |
| T02 | 37 | 0x25 | Zone 1 bis | ÷100 | Oui | ✅ 21.06°C | 2025-01-10 |
| T03 | 38 | 0x26 | Zone 2 | ÷100 | Oui | ✅ 20.00°C | 2025-01-10 |
| T04 | 39 | 0x27 | Zone 3 | ÷100 | Oui | ✅ 21.43°C | 2025-01-10 |
| T05 | 40 | 0x28 | Zone 4 | ÷100 | Oui | ✅ 21.18°C | 2025-01-10 |
| T06 | 41 | 0x29 | Zone 5 | ÷100 | Oui | ✅ 20.18°C | 2025-01-10 |

**Note** : Sur RBUV, R36-41 = températures zones. R36/R37 = même thermostat (Zone 1). Différent de TOUG où R39 = T° extérieure.

### 1.4 Températures PAC internes

| ID | Reg | Hex | Description | Diviseur | Signé | Résultat | Date |
|----|-----|-----|-------------|----------|-------|----------|------|
| P01 | 42 | 0x2A | T° échangeur ext (ThoR1) | ÷100 | Oui | ⚠️ 0.00°C | 2025-01-10 |
| P02 | 44 | 0x2C | T° sortie compresseur TOUG | ÷100 | Non | ❌ 592.71°C | 2025-01-10 |
| P03 | 111 | 0x6F | T° air repris UI | ÷100 | Oui | ✅ 22.28°C | 2025-01-10 |
| P04 | 112 | 0x70 | T° extérieure | ÷100 | Oui | ✅ 8.38°C | 2025-01-10 |
| P05 | 114 | 0x72 | T° échangeur UI | ÷100 | Oui | ✅ 35.38°C | 2025-01-10 |
| P06 | 115 | 0x73 | T° échangeur UE | ÷100 | Oui | ✅ 3.84°C | 2025-01-10 |
| P07 | 117 | 0x75 | T° sortie compresseur | ÷100 | Non | ✅ 46.40°C | 2025-01-10 |

**Note** : R44 retourne une valeur aberrante (592°C). Diviseur différent ou registre non implémenté sur RBUV.

### 1.5 Ventilation / Compresseur

| ID | Reg | Hex | Description | Diviseur | Résultat | Date |
|----|-----|-----|-------------|----------|----------|------|
| V01 | 49 | 0x31 | Courant compresseur | ÷100 | ✅ 2 A | 2025-01-10 |
| V02 | 60 | 0x3C | Consigne ventilateur | 1 | ✅ 560 rpm | 2025-01-10 |
| V03 | 61 | 0x3D | Vitesse ventilateur | 1 | ✅ 561 rpm | 2025-01-10 |
| V04 | 65 | 0x41 | Consigne fréquence | ÷10 | ✅ 38.0 Hz | 2025-01-10 |
| V05 | 66 | 0x42 | Fréquence compresseur | ÷10 | ✅ 38.0 Hz | 2025-01-10 |
| V06 | 72-73 | 0x48 | Temps ON compresseur (32-bit) | 1 | ✅ 2220 s | 2025-01-10 |
| V07 | 91 | 0x5B | Position EEV1 (TOUG) | 1 | ⚠️ 0 (non implémenté RBUV) | 2025-01-10 |
| V08 | 93 | 0x5D | Vitesse ventilateur UE (TOUG) | 1 | ⚠️ 0 (non implémenté RBUV) | 2025-01-10 |
| V09 | 104 | 0x68 | EEV1 (RBUV) | 1 | ✅ 234 Pls | 2025-01-10 |
| V10 | 105 | 0x69 | EEV2 | 1 | ✅ 0 Pls | 2025-01-10 |
| V11 | 106 | 0x6A | Niveau ventilation UE | 1 | ✅ 5 | 2025-01-10 |
| V12 | 125 | 0x7D | Heures ventilateur | 1 | ✅ 25500 h | 2025-01-10 |
| V13 | 127 | 0x7F | Heures compresseur | 1 | ✅ 12600 h | 2025-01-10 |

**Note** : R91 et R93 sont des registres TOUG qui retournent 0 sur RBUV. Utiliser R104/R105 pour EEV sur RBUV.

### 1.6 Débits / Pressions

| ID | Reg | Hex | Description | Unité | Résultat | Date |
|----|-----|-----|-------------|-------|----------|------|
| D01 | 247 | 0xF7 | PSE débit nominal | Pa | ✅ 23 Pa | 2025-01-10 |
| D02 | 248 | 0xF8 | PSE débit mini | Pa | ✅ 12 Pa | 2025-01-10 |
| D03 | 249 | 0xF9 | Débit 1 bouche | m³/h | ✅ 240 m³/h | 2025-01-10 |
| D04 | 250 | 0xFA | Débit nominal | m³/h | ✅ 900 m³/h | 2025-01-10 |
| D05 | 251 | 0xFB | Pression statique ext | Pa | ✅ 18 Pa | 2025-01-10 |

### 1.7 Registres étendus TOUG

| ID | Reg | Description | TOUG | Résultat RBUV | Date |
|----|-----|-------------|------|---------------|------|
| E01 | 5029 | Canaux actifs | ✅ | ❌ 0 (non implémenté) | 2025-01-10 |
| E02 | 6021 | État circuit frigo | ✅ | ❌ 0 (non implémenté) | 2025-01-10 |
| E03 | 20063 | État filtres | ✅ | ❌ 0 (non implémenté) | 2025-01-10 |
| E04 | 30026 | Nb zones configurées | ✅ | ❌ 0 (non implémenté) | 2025-01-10 |
| E05 | 31100 | Consigne Zone K1a | ✅ | ❌ 0 (KO tous modèles) | 2025-01-10 |
| E06 | 31101 | Consigne Zone K1b | ✅ | ❌ 0 (KO tous modèles) | 2025-01-10 |
| E07 | 31102 | Consigne Zone K2 | ✅ | ❌ 0 (KO tous modèles) | 2025-01-10 |
| E08 | 31103 | Consigne Zone K3 | ✅ | ❌ 0 (KO tous modèles) | 2025-01-10 |
| E09 | 31104 | Consigne Zone K4 | ✅ | ❌ 0 (KO tous modèles) | 2025-01-10 |

> **Conclusion** : Les registres étendus TOUG (5029, 6021, 20063, 30026) et les consignes (31100-31104) ne sont **pas implémentés** sur le firmware 3019 RBUV. Confirmé par @djtef que R31100-31104 ne fonctionnent sur **aucun modèle**.

### 1.8 Exploration registres non documentés (2025-01-12)

> **Objectif** : Découvrir des registres non documentés dans TOUG, basé sur recherche web (projet guix77, communauté Jeedom).
> **Rapport détaillé** : `results/rapport_recherche_registres_2025-01-12.md`

#### 1.8.1 Tests préliminaires

| ID | Test | Résultat | Date |
|----|------|----------|------|
| N01 | Adresse esclave 2 | ❌ No communication (confirmé = 1) | 2025-01-12 |
| N02 | Magic number Aldes R0-R3 | ❌ Absent (R1 = firmware 3019) | 2025-01-12 |
| N03 | Registres guix77 (R120, R122, R150...) | ✅ Existent, sens différent | 2025-01-12 |
| N04 | R131 compteur temps | ✅ +1/seconde (temps compresseur) | 2025-01-12 |
| N05 | R136 miroir R131 | ✅ Même valeur que R131 | 2025-01-12 |
| N06 | Scan R0-R500 | ✅ 203 registres trouvés | 2025-01-12 |

#### 1.8.2 Registres découverts - Compteurs temps

| Reg | Valeur exemple | Description | Statut |
|-----|----------------|-------------|--------|
| R131 | 44069 (12h14m) | Compteur secondes compresseur | ✅ Validé |
| R136 | 44069 | Miroir R131 | ✅ Validé |
| R160 | 103 | Compteur lent ? | 🔍 À valider |

#### 1.8.3 Registres découverts - Températures/Consignes

| Reg | Valeur | Hypothèse | Statut |
|-----|--------|-----------|--------|
| R70 | 20.00°C | Consigne générale ? | 🔍 À valider console |
| R101 | 20.00°C | = R70 = R210 | 🔍 À valider console |
| R111 | 18.51°C | T° ambiante moyenne | 🔍 À valider console |
| R120 | 16.00°C / 0 | **Dynamique** (dépend état PAC) | 🔍 À valider console |
| R204 | 23.84°C | Température interne | 🔍 À valider console |
| R210 | 20.00°C | = R70 = R101 | 🔍 À valider console |

#### 1.8.4 Registres découverts - Zone R300+ (jamais documentée)

| Reg | Valeur | Hypothèse | Statut |
|-----|--------|-----------|--------|
| R317-R322 | 2-5 | États/flags par zone ? | 🔍 À identifier |
| R362 | 16.00°C | Seuil bas / antigel ? | 🔍 À valider console |
| R363 | 24.00°C | Seuil haut été ? | 🔍 À valider console |
| R364 | 22.00°C | Consigne clim ? | 🔍 À valider console |
| R365 | 31.00°C | Seuil alarme ? | 🔍 À valider console |
| R374 | 2.00°C | Hystérésis ? | 🔍 À valider console |

#### 1.8.5 Tests à faire sur console PAC

| ID | Test | Registres | Comment valider |
|----|------|-----------|-----------------|
| N07 | Consigne affichée = 20°C ? | R70/R101/R210 | Lire écran PAC |
| N08 | R120 change avec mode | R120 | Basculer Eco ↔ Confort |
| N09 | R362-R365 = seuils menu ? | R362-R365 | Chercher dans paramètres |
| N10 | R204 = quelle température ? | R204 | Comparer avec écran |
| N11 | Identifier R317-R322 | R317-R322 | Observer si change avec zones |

---

## 2. Tests écriture Modbus standard

> **Résultat attendu** : Échec sur tous les tests. Ces tests confirment que l'écriture standard ne fonctionne pas.

| ID | Reg | FC | Bus | Attendu | Résultat | Date |
|----|-----|-----|-----|---------|----------|------|
| W01 | 9 | 0x06 | USB | illegal function | ✅ illegal function | 2025-01-10 |
| W02 | 9 | 0x10 | USB | illegal data address | ✅ illegal data address | 2025-01-10 |
| W03 | 9 | 0x06 | RS485 | illegal function | ⬜ | |
| W04 | 9 | 0x10 | RS485 | illegal data address | ⬜ | |
| W05 | 20 | 0x06 | USB | illegal data address | ✅ illegal data address | 2025-01-10 |
| W06 | 31100 | 0x06 | USB | illegal data address | ✅ illegal data address | 2025-01-10 |
| W07 | 31101 | 0x06 | USB | illegal data address | ✅ illegal data address | 2025-01-10 |
| W08 | 31102 | 0x06 | USB | illegal data address | ✅ illegal data address | 2025-01-10 |
| W09 | 31103 | 0x06 | USB | illegal data address | ✅ illegal data address | 2025-01-10 |
| W10 | 31104 | 0x06 | USB | illegal data address | ✅ illegal data address | 2025-01-10 |

### 2.2 Tests FC16 (Write Multiple Registers) - USB (2025-01-12)

> **Objectif** : Vérifier si FC16 permet d'écrire sur certains registres via USB.
> **Rapport détaillé** : `results/rapport_recherche_registres_2025-01-12.md`

| ID | Registres | FC16 | Observation | Date |
|----|-----------|------|-------------|------|
| W11 | R20-R25 (consignes zones) | ❌ illegal data address | Confirmé lecture seule | 2025-01-12 |
| W12 | R362-R374 (seuils) | ❌ illegal data address | Non accessibles en écriture | 2025-01-12 |
| W13 | R90,R92,R94,R96 | ✅ Accepté | Stats/compteurs ? | 2025-01-12 |
| W14 | R101,R102 | ✅ Accepté | R101=20.0°C (consigne?) | 2025-01-12 |
| W15 | R104,R107,R108,R110 | ✅ Accepté | EEV/flags | 2025-01-12 |
| W16 | R111-R115,R117 | ✅ Accepté | Températures PAC | 2025-01-12 |

**Total : 16 registres acceptent FC16** (R90, R92, R94, R96, R101, R102, R104, R107, R108, R110, R111-R115, R117)

#### ⚠️ ATTENTION : Faille du test

Ces tests ont écrit LA MÊME valeur que celle lue. Cela ne prouve pas que l'écriture est effective.
La PAC peut accepter la commande mais ignorer le contenu.

### 2.3 Tests FC16 avec valeur différente - ✅ EFFECTUÉS (2025-01-12)

| ID | Test | Registre | Avant | Écrit | Après | Résultat | Date |
|----|------|----------|-------|-------|-------|----------|------|
| W17 | FC16 valeur différente | R107 | 129 | 254 | 30 | ❌ Dynamique | 2025-01-12 |
| W18 | FC16 valeur différente | R108 | 16 | 254 | 255 | ❌ Dynamique | 2025-01-12 |
| W19 | FC16 valeur différente | R110 | 255 | 254 | 255 | ❌ Ignoré | 2025-01-12 |

### ✅ Conclusion finale écriture USB

**Le bus USB est LECTURE SEULE sur firmware 3019 RBUV.**

| Function Code | Résultat |
|---------------|----------|
| FC06 (Write Single) | "illegal function" |
| FC16 (Write Multiple) | Accepté mais **ignoré** |

**Seule option écriture confirmée : Protocole 0x17 sur bus RS485 télécommande.**

**Découverte bonus** : R107/R108 sont des registres dynamiques (capteurs temps réel), pas des flags à 255

---

## 3. Tests protocole 0x17 (spécifique RBUV)

### 3.0 Structure trame 0x17 (74 bytes)

> **Référence** : Validé par sniffing 2025-01-13

| Offset | Taille | Description | Valeurs connues |
|--------|--------|-------------|-----------------|
| 0 | 1 | Adresse Modbus | 0x01 |
| 1 | 1 | Fonction | 0x17 (Read/Write Multiple) |
| 2-3 | 2 | Sous-code séquence | 0x0081→0x00C1→0x0001→0x0041 (cycle) |
| 4-5 | 2 | Longueur | 0x0040 (64) |
| 6-7 | 2 | Constante | 0x0057 |
| 8-9 | 2 | Constante | 0x001F |
| 10-11 | 2 | Signature | 0x7370 ("sp") |
| 12-13 | 2 | Version | 0x1804 |
| 14-15 | 2 | Compteur | Incrémente à chaque trame |
| 16-17 | 2 | ? | 0xF67A observé |
| **18-19** | 2 | **Niveau** | 0x0000=Confort, 0x00C8=Eco, 0x5678=Boost |
| 20-25 | 6 | Padding ? | 0x0000 |
| **26-27** | 2 | **Débit nominal** | ✅ 0x0384=900 m³/h |
| **28-29** | 2 | **PSE nominal** | ✅ 0x0017=23 Pa |
| 30-31 | 2 | ? | 0x00F0=240 (débit mini ?) |
| **32-33** | 2 | **Type mode** | ✅ 0x000C=Chauffage, 0x000A=Clim |
| **34-35** | 2 | **Vacances** | 0x0000=Off, 0x1234=On |
| **36-37** | 2 | **On/Off** | ✅ 0x0002=Off, 0x0003=On |
| 38-39 | 2 | Type mode (copie?) | 0x000C |
| 40-69 | 30 | Consignes zones | Pattern 0x7FFE = pas de changement |
| 70-71 | 2 | ? | 0x0000 |
| 72-73 | 2 | CRC16 Modbus | Calculé |

> ⚠️ **Correction 2025-01-13** : Offsets 32-37 corrigés suite au sniffing X01

### 3.1 Sniffing télécommande

**Matériel** : Pi 2B + Waveshare RS485 connecté **directement** à la télécommande

**Configuration** :
- Télécommande **DÉBRANCHÉE** de la PAC
- Waveshare RS485 connecté aux bornes A/B de la télécommande
- Permet de capturer uniquement les trames émises (sans réponses PAC)

**Connexion** :
```
Télécommande          Waveshare RS485 (Pi 2B)
    A  ───────────────  A
    B  ───────────────  B
   GND ───────────────  GND
```

**Commande capture** :
```bash
# Méthode simple
stty -F /dev/ttyUSB0 19200 cs8 parenb -parodd -cstopb raw -echo
timeout 30 cat /dev/ttyUSB0 > /tmp/capture.bin
# Appuyer sur boutons télécommande pendant la capture
xxd /tmp/capture.bin

# Ou avec script (si disponible)
python3 tests/sniff_rs485.py --output capture.bin
```

#### 3.1.1 Modes PAC (On/Off, Chauffage/Clim)

| ID | Action télécommande | Offset | Valeur attendue | Résultat | Date |
|----|---------------------|--------|-----------------|----------|------|
| X01 | Chauffage Confort → Off | **36-37** | 0x0002 | ✅ | 2025-01-13 |
| X02 | Off → Chauffage Confort | 36-37 | 0x0003 | ✅ | 2025-01-13 |
| X03 | Confort → Eco | 18-19 | 0x00C8 | ✅ | 2025-01-13 |
| X04 | Eco → Confort | 18-19 | 0x0000 | ✅ | 2025-01-13 |
| X05 | Chauffage → Clim | **38-39** | 0x000A | ✅ | 2025-01-13 |
| X06 | Clim → Chauffage | **38-39** | 0x000C | ✅ | 2025-01-13 |
| X07 | Clim Confort → Boost | **20-21** | 0x5678 | ✅ | 2025-01-13 |
| X08 | Vacances On | 34-35 | 0x1234 | ✅ | 2025-01-13 |
| X09 | Vacances Off | 34-35 | 0x0000 | ⬜ | |
| X10 | Cycle sous-codes | 2-3 | 01→41→81→C1 | ⬜ | |

#### 3.1.2 Ventilation / Débits

> **Objectif** : Valider les offsets supposés (28-31) et trouver les autres.

| ID | Action télécommande | Offset supposé | Valeur attendue | Résultat | Date |
|----|---------------------|----------------|-----------------|----------|------|
| X11 | Menu → Débit nominal ↑ | 28-29 | Incrémenté (+20) | ⬜ | |
| X12 | Menu → Débit nominal ↓ | 28-29 | Décrémenté (-20) | ⬜ | |
| X13 | Menu → PSE nominal ↑ | 30-31 | Incrémenté (+1) | ⬜ | |
| X14 | Menu → PSE nominal ↓ | 30-31 | Décrémenté (-1) | ⬜ | |
| X15 | Menu → Débit mini ↑ | ? | Chercher offset | ⬜ | |
| X16 | Menu → Débit mini ↓ | ? | Chercher offset | ⬜ | |
| X17 | Menu → PSE mini ↑ | ? | Chercher offset | ⬜ | |
| X18 | Menu → PSE mini ↓ | ? | Chercher offset | ⬜ | |

#### 3.1.3 Date/Heure

> **Objectif** : Déterminer si la date/heure est transmise dans la trame 0x17 et à quel offset.
> **Note** : R16/R17 non fonctionnels via USB, la date/heure pourrait être dans la trame 0x17.

| ID | Action télécommande | Offset recherché | Observation | Résultat | Date |
|----|---------------------|------------------|-------------|----------|------|
| X19 | Capture sans changement | 14-17 ? 20-27 ? | Noter valeurs actuelles | ⬜ | |
| X20 | Changement heure +1h | ? | Chercher bytes modifiés | ⬜ | |
| X21 | Changement date +1j | ? | Chercher bytes modifiés | ⬜ | |
| X22 | Changement année | ? | Chercher bytes modifiés | ⬜ | |
| X23 | Format encodage | ? | BCD ? Unix ? Custom ? | ⬜ | |

#### 3.1.4 Consignes thermostats

> **Note** : Les consignes sont pilotées par thermostats radio 868MHz. Ce test vérifie si la télécommande peut aussi les modifier via 0x17.
> **Hypothèse** : Offset 40-69 contient les consignes, pattern 0x7FFE = "pas de changement"

| ID | Action télécommande | Offset supposé | Observation | Résultat | Date |
|----|---------------------|----------------|-------------|----------|------|
| X24 | Capture trame normale | 40-69 | Noter pattern (0x7FFE?) | ⬜ | |
| X25 | Menu consigne zone 1 ↑ | 40-41 ? | Chercher changement | ⬜ | |
| X26 | Menu consigne zone 1 ↓ | 40-41 ? | Chercher changement | ⬜ | |
| X27 | Consigne différente par zone | 40-69 | Identifier mapping | ⬜ | |

#### 3.1.5 Analyse trame complète

| ID | Test | Description | Résultat | Date |
|----|------|-------------|----------|------|
| X28 | Dump trame 74 bytes | Capturer et annoter tous les octets | ⬜ | |
| X29 | Comparer trames successives | Identifier bytes qui changent | ⬜ | |
| X30 | Valider CRC | Vérifier calcul CRC16 Modbus (octets 72-73) | ⬜ | |
| X31 | Identifier octets inconnus | Offsets 14-17, 20-27, 38-39, 70-71 | ⬜ | |

### 3.2 Envoi trame (ESP32 → PAC)

**Prérequis** : Télécommande DÉBRANCHÉE

#### 3.2.1 Modes PAC (implémenté dans aldes_tone.h)

| ID | Mode envoyé | Trame (niveau, vacances, onoff, type) | Vérif R9 USB | Résultat | Date |
|----|-------------|---------------------------------------|--------------|----------|------|
| Y01 | Off | (0x0000, 0x0000, 0x0002, 0x000C) | R9 = 5 | ⬜ | |
| Y02 | Chauffage Confort | (0x0000, 0x0000, 0x0003, 0x000C) | R9 = 4 | ⬜ | |
| Y03 | Chauffage Eco | (0x00C8, 0x0000, 0x0003, 0x000C) | R9 = 4 | ⬜ | |
| Y04 | Clim Confort | (0x0000, 0x0000, 0x0003, 0x000A) | R9 = 2 | ⬜ | |
| Y05 | Clim Boost | (0x5678, 0x0000, 0x0003, 0x000A) | R9 = 2 | ⬜ | |
| Y06 | Vacances On | (0x0000, 0x1234, 0x0003, 0x000C) | Comportement ? | ⬜ | |
| Y07 | Vacances Off | (0x0000, 0x0000, 0x0003, 0x000C) | Retour normal | ⬜ | |

#### 3.2.2 Ventilation / Débits (à implémenter)

> **Note** : Nécessite d'abord valider les offsets via sniffing (X11-X18)

| ID | Paramètre | Offset | Vérif registre USB | Résultat | Date |
|----|-----------|--------|-------------------|----------|------|
| Y08 | Débit nominal 900→880 | 28-29 | R250 = 880 ? | ⬜ | |
| Y09 | Débit nominal 880→900 | 28-29 | R250 = 900 ? | ⬜ | |
| Y10 | PSE nominal 23→25 | 30-31 | R247 = 25 ? | ⬜ | |
| Y11 | PSE nominal 25→23 | 30-31 | R247 = 23 ? | ⬜ | |
| Y12 | Débit mini (après sniff) | ? | R249 ? | ⬜ | |
| Y13 | PSE mini (après sniff) | ? | R248 ? | ⬜ | |

#### 3.2.3 Date/Heure (à implémenter si trouvé)

> **Note** : Nécessite d'abord identifier l'offset via sniffing (X19-X23)

| ID | Test | Vérification | Résultat | Date |
|----|------|--------------|----------|------|
| Y14 | Écriture heure | Écran PAC ? R16/R17 ? | ⬜ | |
| Y15 | Écriture date | Écran PAC ? R16/R17 ? | ⬜ | |

### 3.3 Réponses PAC

| ID | Test | Attendu | Résultat | Date |
|----|------|---------|----------|------|
| Z01 | Format réponse principale | 0117 80xx | ⬜ | |
| Z02 | Format données additionnelles | 0117 78xx | ⬜ | |
| Z03 | Délai réponse | < 100ms ? | ⬜ | |
| Z04 | Contenu réponse | Quelles données ? | ⬜ | |
| Z05 | Acquittement écriture | ACK explicite ou données ? | ⬜ | |

---

## 4. Commandes de test

### Scripts automatisés

```bash
# Lecture tous les registres RBUV
python3 tests/read_registers.py --port /dev/ttyACM1

# Lecture avec registres TOUG
python3 tests/read_registers.py --port /dev/ttyACM1 --toug

# Lecture groupe spécifique
python3 tests/read_registers.py --port /dev/ttyACM1 --group system

# Test écriture Modbus (échec attendu)
python3 tests/test_write_modbus.py --port /dev/ttyACM1

# Sniff RS485 télécommande
python3 tests/sniff_rs485.py --output capture.bin

# Décoder une trame 0x17
python3 tests/decode_frame_0x17.py capture.bin
```

### Lecture registre manuel

```bash
python3 -c "
import minimalmodbus
instr = minimalmodbus.Instrument('/dev/ttyACM1', 1)
instr.serial.baudrate = 1200
instr.serial.parity = 'E'
instr.serial.timeout = 1
print(f'R9 (mode): {instr.read_register(9)}')
"
```

---

## 5. Template résultat

Fichier : `results/YYYY-MM-DD_ID-description.md`

```markdown
# Test [ID] - [Description]

**Date** : YYYY-MM-DD HH:MM
**Testeur** : [nom]
**Matériel** : Pi Zero 2 W / Pi 2B / ESP32

## Commande

\`\`\`bash
[commande exécutée]
\`\`\`

## Sortie

\`\`\`
[sortie brute]
\`\`\`

## Résultat

- [ ] ✅ PASS
- [ ] ❌ FAIL
- [ ] ⚠️ PARTIAL

## Notes

[observations, anomalies, etc.]
```

---

## Légende

| Symbole | Signification |
|---------|---------------|
| ⬜ | Non testé |
| ✅ | Fonctionne |
| ❌ | Ne fonctionne pas |
| ⚠️ | Partiel / comportement différent |

---

*Documentation TOUG_RBUV - Tests - Mise à jour 2025-01-12*
