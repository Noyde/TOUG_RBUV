# Tests TOUG_RBUV

Matrice de tests pour valider le fonctionnement sur PAC Aldes T.One RBUV (modèles 2018).

> **Objectif** : Comparer les registres documentés dans TOUG (djtef) avec ce qui fonctionne réellement sur le modèle RBUV.

---

## Prérequis

### Matériel

| Équipement | Usage | Port |
|------------|-------|------|
| Pi Zero 2 W | Lecture USB | /dev/ttyACM0 |
| Pi 2B + Waveshare RS485 | Sniffing télécommande | /dev/ttyUSB0 |
| ESP32 D1 Mini | Envoi trames 0x17 | GPIO16/17 |

### Conditions

- **Télécommande DÉBRANCHÉE** pour tests écriture (collision bus sinon)
- PAC sous tension et en fonctionnement normal
- Accès SSH aux Pi

### Dépendances Python

```bash
pip install minimalmodbus pyserial
```

---

## 1. Registres lecture (USB 1200 bauds)

### 1.1 Système

| ID | Reg | Hex | Description | Diviseur | TOUG | Résultat | Date |
|----|-----|-----|-------------|----------|------|----------|------|
| S01 | 1 | 0x01 | Version firmware | 1 | ✅ | ⬜ | |
| S02 | 3 | 0x03 | Durée ON (min) | 1 | ✅ | ⬜ | |
| S03 | 9 | 0x09 | Mode PAC | 1 | ✅ | ⬜ | |
| S04 | 14-15 | 0x0E | Panel ID (32-bit) | 1 | ✅ | ⬜ | |
| S05 | 16 | 0x10 | Date encodée | 1 | ✅ | ⬜ | |
| S06 | 17 | 0x11 | Heure encodée | 1 | ✅ | ⬜ | |
| S07 | 51 | 0x33 | Protection compresseur | 1 | ✅ | ⬜ | |
| S08 | 90 | 0x5A | Code défaut UE | 1 | ✅ | ⬜ | |
| S09 | 131 | 0x83 | État dégivrage | 1 | ✅ | ⬜ | |

### 1.2 Consignes thermostats (lecture seule)

| ID | Reg | Hex | Zone | Diviseur | TOUG | Résultat | Date |
|----|-----|-----|------|----------|------|----------|------|
| C01 | 20 | 0x14 | Zone 1 (K1a) | ÷100 | ✅ | ⬜ | |
| C02 | 21 | 0x15 | Zone 1 bis (K1b) | ÷100 | ✅ | ⬜ | |
| C03 | 22 | 0x16 | Zone 2 | ÷100 | ✅ | ⬜ | |
| C04 | 23 | 0x17 | Zone 3 | ÷100 | ✅ | ⬜ | |
| C05 | 24 | 0x18 | Zone 4 | ÷100 | ✅ | ⬜ | |
| C06 | 25 | 0x19 | Zone 5 | ÷100 | ✅ | ⬜ | |

### 1.3 Températures zones

| ID | Reg | Hex | Zone | Diviseur | Signé | Résultat | Date |
|----|-----|-----|------|----------|-------|----------|------|
| T01 | 36 | 0x24 | Zone 1 | ÷100 | Oui | ⬜ | |
| T02 | 37 | 0x25 | Zone 2 | ÷100 | Oui | ⬜ | |
| T03 | 38 | 0x26 | Zone 3 | ÷100 | Oui | ⬜ | |
| T04 | 39 | 0x27 | Zone 4 | ÷100 | Oui | ⬜ | |
| T05 | 40 | 0x28 | Zone 5 | ÷100 | Oui | ⬜ | |
| T06 | 41 | 0x29 | Zone 6 | ÷100 | Oui | ⬜ | |

**Note TOUG** : Sur modèles récents, R39 = T° extérieure, R190-194 = ambiantes. À vérifier sur RBUV.

### 1.4 Températures PAC internes

| ID | Reg | Hex | Description | Diviseur | Signé | Résultat | Date |
|----|-----|-----|-------------|----------|-------|----------|------|
| P01 | 42 | 0x2A | T° échangeur ext (ThoR1) | ÷100 | Oui | ⬜ | |
| P02 | 44 | 0x2C | T° sortie compresseur | ÷100 | Non | ⬜ | |
| P03 | 111 | 0x6F | T° air repris UI | ÷100 | Oui | ⬜ | |
| P04 | 112 | 0x70 | T° extérieure | ÷100 | Oui | ⬜ | |
| P05 | 114 | 0x72 | T° échangeur UI | ÷100 | Oui | ⬜ | |
| P06 | 115 | 0x73 | T° échangeur UE | ÷100 | Oui | ⬜ | |
| P07 | 117 | 0x75 | T° sortie compresseur | ÷100 | Non | ⬜ | |

### 1.5 Ventilation / Compresseur

| ID | Reg | Hex | Description | Diviseur | Résultat | Date |
|----|-----|-----|-------------|----------|----------|------|
| V01 | 49 | 0x31 | Courant compresseur | ÷100 | ⬜ | |
| V02 | 60 | 0x3C | Consigne ventilateur | 1 | ⬜ | |
| V03 | 61 | 0x3D | Vitesse ventilateur | 1 | ⬜ | |
| V04 | 65 | 0x41 | Consigne fréquence | ÷10 | ⬜ | |
| V05 | 66 | 0x42 | Fréquence compresseur | ÷10 | ⬜ | |
| V06 | 72-73 | 0x48 | Temps ON compresseur (32-bit) | 1 | ⬜ | |
| V07 | 91 | 0x5B | Position EEV1 | 1 | ⬜ | |
| V08 | 93 | 0x5D | Vitesse ventilateur UE | 1 | ⬜ | |
| V09 | 104 | 0x68 | EEV1 | 1 | ⬜ | |
| V10 | 105 | 0x69 | EEV2 | 1 | ⬜ | |
| V11 | 106 | 0x6A | Niveau ventilation UE | 1 | ⬜ | |
| V12 | 125 | 0x7D | Heures ventilateur | 1 | ⬜ | |
| V13 | 127 | 0x7F | Heures compresseur | 1 | ⬜ | |

### 1.6 Débits / Pressions

| ID | Reg | Hex | Description | Unité | Résultat | Date |
|----|-----|-----|-------------|-------|----------|------|
| D01 | 247 | 0xF7 | PSE débit nominal | Pa | ⬜ | |
| D02 | 248 | 0xF8 | PSE débit mini | Pa | ⬜ | |
| D03 | 249 | 0xF9 | Débit 1 bouche | m³/h | ⬜ | |
| D04 | 250 | 0xFA | Débit nominal | m³/h | ⬜ | |
| D05 | 251 | 0xFB | Pression statique ext | Pa | ⬜ | |

### 1.7 Registres étendus TOUG

| ID | Reg | Description | TOUG | Attendu RBUV | Résultat | Date |
|----|-----|-------------|------|--------------|----------|------|
| E01 | 5029 | Canaux actifs | ✅ | ? | ⬜ | |
| E02 | 6021 | État circuit frigo | ✅ | ? | ⬜ | |
| E03 | 20063 | État filtres | ✅ | ? | ⬜ | |
| E04 | 20047-48 | Temps ventilateur (32-bit) | ✅ | ? | ⬜ | |
| E05 | 21668-83 | Consommations (32-bit) | ✅ | ? | ⬜ | |
| E06 | 30026 | Nb zones configurées | ✅ | ? | ⬜ | |

---

## 2. Tests écriture Modbus standard

> **Résultat attendu** : Échec sur tous les tests. Ces tests confirment que l'écriture standard ne fonctionne pas.

| ID | Reg | FC | Bus | Attendu | Résultat | Date |
|----|-----|-----|-----|---------|----------|------|
| W01 | 9 | 0x06 | USB | illegal function | ⬜ | |
| W02 | 9 | 0x10 | USB | illegal data address | ⬜ | |
| W03 | 9 | 0x06 | RS485 | illegal function | ⬜ | |
| W04 | 9 | 0x10 | RS485 | illegal data address | ⬜ | |
| W05 | 20 | 0x06 | USB | illegal data address | ⬜ | |
| W06 | 31100 | 0x06 | USB | illegal data address | ⬜ | |
| W07 | 31101 | 0x06 | USB | illegal data address | ⬜ | |
| W08 | 31102 | 0x06 | USB | illegal data address | ⬜ | |
| W09 | 31103 | 0x06 | USB | illegal data address | ⬜ | |
| W10 | 31104 | 0x06 | USB | illegal data address | ⬜ | |

> **Note importante** : Les registres R31100-31104 (consignes zones) ne fonctionnent sur **aucun modèle** T.One, contrairement à ce que suggère la doc TOUG. Confirmé par @djtef.

---

## 3. Tests protocole 0x17 (spécifique RBUV)

### 3.1 Sniffing télécommande

**Matériel** : Pi 2B + Waveshare RS485 en parallèle sur bus télécommande

**Commande capture** :
```bash
stty -F /dev/ttyUSB0 19200 cs8 parenb -parodd -cstopb raw -echo
timeout 30 cat /dev/ttyUSB0 > /tmp/capture.bin
xxd /tmp/capture.bin | head -50
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

### Lecture registre unique

```bash
python3 -c "
import minimalmodbus
instr = minimalmodbus.Instrument('/dev/ttyACM0', 1)
instr.serial.baudrate = 1200
instr.serial.parity = 'E'
instr.serial.timeout = 1
print(f'R9 (mode): {instr.read_register(9)}')
"
```

### Lecture plage de registres

```bash
python3 -c "
import minimalmodbus
instr = minimalmodbus.Instrument('/dev/ttyACM0', 1)
instr.serial.baudrate = 1200
instr.serial.parity = 'E'
instr.serial.timeout = 1
for r in [1, 3, 9, 20, 21, 22, 23, 24, 25]:
    try:
        val = instr.read_register(r)
        print(f'R{r}: {val}')
    except Exception as e:
        print(f'R{r}: ERREUR - {e}')
"
```

### Test écriture (échec attendu)

```bash
python3 -c "
import minimalmodbus
instr = minimalmodbus.Instrument('/dev/ttyACM0', 1)
instr.serial.baudrate = 1200
instr.serial.parity = 'E'
instr.serial.timeout = 1
try:
    instr.write_register(9, 4)  # FC 0x06
    print('ERREUR: écriture acceptée (inattendu)')
except Exception as e:
    print(f'OK: {e}')
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
| ? | Inconnu / à vérifier |

---

*Documentation TOUG_RBUV - Tests*
