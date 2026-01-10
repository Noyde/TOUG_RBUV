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

## Résumé des tests (2025-01-10)

| Groupe | Total | OK | KO | Notes |
|--------|-------|----|----|-------|
| RBUV (34 registres) | 34 | 34 | 0 | ✅ Tous fonctionnent |
| TOUG System | 7 | 7 | 0 | Valeurs à interpréter |
| TOUG Temperatures | 3 | 3 | 0 | R44 valeur aberrante |
| TOUG Ventilation | 4 | 4 | 0 | R91/R93 = 0 |
| TOUG Extended | 4 | 0 | 4 | ❌ Non implémentés (tous = 0) |
| TOUG Consignes | 5 | 0 | 5 | ❌ Confirmé KO (tous = 0) |

---

## 1. Registres lecture (USB 1200 bauds)

### 1.1 Système

| ID | Reg | Hex | Description | Diviseur | TOUG | Résultat | Date |
|----|-----|-----|-------------|----------|------|----------|------|
| S01 | 1 | 0x01 | Version firmware | 1 | ✅ | ✅ 3019 | 2025-01-10 |
| S02 | 3 | 0x03 | Durée ON (min) | 1 | ✅ | ✅ 36 min | 2025-01-10 |
| S03 | 9 | 0x09 | Mode PAC | 1 | ✅ | ✅ 4 (Chauffage) | 2025-01-10 |
| S04 | 14-15 | 0x0E | Panel ID (32-bit) | 1 | ✅ | ✅ 1, 0 | 2025-01-10 |
| S05 | 16 | 0x10 | Date encodée | 1 | ✅ | ✅ 4883 | 2025-01-10 |
| S06 | 17 | 0x11 | Heure encodée | 1 | ✅ | ✅ 4864 | 2025-01-10 |
| S07 | 51 | 0x33 | Protection compresseur | 1 | ✅ | ✅ 243 | 2025-01-10 |
| S08 | 90 | 0x5A | Code défaut UE | 1 | ✅ | ⚠️ 700 | 2025-01-10 |
| S09 | 131 | 0x83 | État dégivrage | 1 | ✅ | ⚠️ 11274 | 2025-01-10 |

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
| T02 | 37 | 0x25 | Zone 2 | ÷100 | Oui | ✅ 21.06°C | 2025-01-10 |
| T03 | 38 | 0x26 | Zone 3 | ÷100 | Oui | ✅ 20.00°C | 2025-01-10 |
| T04 | 39 | 0x27 | Zone 4 | ÷100 | Oui | ✅ 21.43°C | 2025-01-10 |
| T05 | 40 | 0x28 | Zone 5 | ÷100 | Oui | ✅ 21.18°C | 2025-01-10 |
| T06 | 41 | 0x29 | Zone 6 | ÷100 | Oui | ✅ 20.18°C | 2025-01-10 |

**Note** : Sur RBUV, R36-41 = températures zones. Différent de TOUG où R39 = T° extérieure.

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
| V07 | 91 | 0x5B | Position EEV1 | 1 | ⚠️ 0 | 2025-01-10 |
| V08 | 93 | 0x5D | Vitesse ventilateur UE | 1 | ⚠️ 0 | 2025-01-10 |
| V09 | 104 | 0x68 | EEV1 | 1 | ✅ 234 Pls | 2025-01-10 |
| V10 | 105 | 0x69 | EEV2 | 1 | ✅ 0 Pls | 2025-01-10 |
| V11 | 106 | 0x6A | Niveau ventilation UE | 1 | ✅ 5 | 2025-01-10 |
| V12 | 125 | 0x7D | Heures ventilateur | 1 | ✅ 25500 h | 2025-01-10 |
| V13 | 127 | 0x7F | Heures compresseur | 1 | ✅ 12600 h | 2025-01-10 |

**Note** : R91 et R93 retournent 0. Registres différents ou non implémentés sur RBUV.

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

---

## 3. Tests protocole 0x17 (spécifique RBUV)

### 3.1 Sniffing télécommande

**Matériel** : Pi 2B + Waveshare RS485 en parallèle sur bus télécommande

**Commande capture** :
```bash
python3 tests/sniff_rs485.py --output capture.bin
```

| ID | Action télécommande | Offset | Valeur attendue | Résultat | Date |
|----|---------------------|--------|-----------------|----------|------|
| X01 | Chauffage Confort → Off | 34-35 | 0x0002 | ⬜ | |
| X02 | Off → Chauffage Confort | 34-35 | 0x0003 | ⬜ | |
| X03 | Confort → Eco | 18-19 | 0x00C8 | ⬜ | |
| X04 | Eco → Confort | 18-19 | 0x0000 | ⬜ | |
| X05 | Chauffage → Clim | 36-37 | 0x000A | ⬜ | |
| X06 | Clim → Chauffage | 36-37 | 0x000C | ⬜ | |
| X07 | Clim Confort → Boost | 18-19 | 0x5678 | ⬜ | |
| X08 | Vacances On | 32-33 | 0x1234 | ⬜ | |
| X09 | Vacances Off | 32-33 | 0x0000 | ⬜ | |
| X10 | Cycle sous-codes | 2-3 | 01→41→81→C1 | ⬜ | |

### 3.2 Envoi trame (ESP32 → PAC)

**Prérequis** : Télécommande DÉBRANCHÉE

| ID | Mode envoyé | Vérif R9 USB | Résultat | Date |
|----|-------------|--------------|----------|------|
| Y01 | Off | R9 = 5 | ⬜ | |
| Y02 | Chauffage Confort | R9 = 4 | ⬜ | |
| Y03 | Chauffage Eco | R9 = 4 | ⬜ | |
| Y04 | Clim Confort | R9 = 2 | ⬜ | |
| Y05 | Clim Boost | R9 = 2 | ⬜ | |
| Y06 | Vacances On | Comportement ? | ⬜ | |
| Y07 | Vacances Off | Retour normal | ⬜ | |

### 3.3 Réponses PAC

| ID | Test | Attendu | Résultat | Date |
|----|------|---------|----------|------|
| Z01 | Format réponse principale | 0117 80xx | ⬜ | |
| Z02 | Format données additionnelles | 0117 78xx | ⬜ | |
| Z03 | Délai réponse | < 100ms ? | ⬜ | |

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

*Documentation TOUG_RBUV - Tests - Mise à jour 2025-01-10*
