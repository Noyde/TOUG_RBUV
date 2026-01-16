# Protocole USB Box Connect (Découverte djtef - Janvier 2025)

> **Source** : Analyse par @djtef via sniffing USB d'une passerelle Box Connect Aldes
> **Statut** : Non testé sur RBUV - À valider

## Résumé

Protocole propriétaire utilisé par la passerelle Box Connect Aldes pour communiquer avec les PAC T.One via USB. Ce protocole est **différent** du Modbus standard utilisé actuellement sur le RBUV à 1200 bauds.

## Comparaison avec le protocole actuel

| Paramètre | RBUV 2018 (actuel) | Box Connect (djtef) |
|-----------|-------------------|---------------------|
| Baudrate | 1200 | **115200** |
| Parité | EVEN | **Aucune** |
| Bits | 8 | 8 |
| Stop | 1 | 1 |
| Protocole | Modbus 0x03 | **Propriétaire** |
| Écriture | ❌ Impossible | ✅ Possible |
| Keep-alive | Non requis | **Obligatoire** |

## Structure des trames

### Format universel

```
[HEADER 2 bytes] [LONGUEUR 1 byte] [FF] [TYPE/ID] [DONNÉES...] [CHECKSUM]
```

### Types de headers

| Header | Direction | Description |
|--------|-----------|-------------|
| `FA FD` | PAC → Passerelle | Message sortant (Monitoring/Info) |
| `FD FA` | Passerelle → PAC | Message entrant (Commandes/Requêtes) |
| `FF FD` | PAC → Passerelle | Réponse directe à une commande |

## Keep-Alive (Dialogue de maintien)

La PAC exige un échange Ping/Pong pour accepter les communications "normales".

### Ping (envoyé par la PAC)

```
FA FD 07 FF 4A FE BB
```

Émis toutes les 2 à 20 secondes par la PAC.

### Pong (réponse de la passerelle)

```
FD FA 07 FF 13 FE F2
```

### Initialisation (passerelle → PAC)

```
02 03 04 20 00 01 02 42 A2
```

Cette trame force la PAC à passer du mode Debug (175 octets) au mode Standard (112 octets).

## Types de rapports

| ID (Hex) | Longueur | Nom | Contenu |
|----------|----------|-----|---------|
| 0x21 | 64 oct | Configuration | Consignes cibles, modes de marche |
| 0x22 | 112 oct | Monitoring | Températures sondes, vitesses ventilateurs |
| 0x23 | 119 oct | Programmation | Grille horaire 7j/24h (bitmaps) |
| 0x25 | 175 oct | Full Debug | Rapport verbeux (défaut, beaucoup de 0x00) |

## Encodage des données

### Températures (16 bits Little Endian)

Les valeurs sont en **degrés Celsius × 100**.

| Octets (LE) | Hex (BE) | Décimal | Température |
|-------------|----------|---------|-------------|
| `D0 07` | `07 D0` | 2000 | 20.00°C |
| `6C 07` | `07 6C` | 1900 | 19.00°C |
| `48 08` | `08 48` | 2120 | 21.20°C |

### Programmation horaire (Type 0x23)

Même format que le Modbus télécommande (registres 31200 à 31255) :

- Chaque jour = 4 octets (32 bits)
- LSB (00h-15h) : 16 bits pour les 16 premières heures
- MSB (16h-23h) : 8 bits pour les 8 dernières heures
- Bit à 1 = Mode Confort
- Bit à 0 = Mode Éco

## Commandes de lecture (Polling)

### Lire les consignes (Type 0x21)

Méthode propriétaire :
```
FD FA 08 FF 41 21 FE A2
```

Méthode Modbus encapsulée :
```
02 03 04 20 00 01 84 C3
```

### Lire la programmation horaire (Type 0x23)

```
FD FA 08 FF 42 22 FE A0
```

L'ID 0x42 demande le rapport suivant le 0x22.

## Écriture de paramètres

### Structure trame d'écriture (Type 0x58)

La passerelle envoie une trame contenant :

1. **Liste complète** des paramètres
2. Valeurs non modifiées remplies avec `FF FF` (masquage)
3. Valeur cible injectée (ex: `D0 07` pour 20.00°C)

### Confirmation

La PAC répond par une trame `FF FD` de type 0x21 pour confirmer.

## Fin de trame et synchronisation

Chaque rapport se termine par un bloc de 26 octets incluant :

| Offset | Longueur | Description |
|--------|----------|-------------|
| 14-17 | 4 bytes | Timestamp Unix (compteur secondes) |
| - | Variable | État des relais |
| - | Variable | Erreurs actives |
| Fin | 2 bytes | Checksum (commence par `FE` + 1 octet) |

### Exemple timestamp

```
F9 A2 30 5C → 0x5C30A2F9 → 1546699513 → 2019-01-05 14:45:13 UTC
```

## Hypothèse architecture interne

Selon @djtef, il y aurait :

- **Un bus interne unique** avec logique "objet"
- **Plusieurs façades** : télécommande, USB, Modbus utilisateur
- **Même sémantique métier** encapsulée différemment

```
                    ┌─────────────────────┐
                    │   Bus interne PAC   │
                    │   (Registres/Objets)│
                    └─────────┬───────────┘
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
       ▼                      ▼                      ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Télécommande │    │     USB      │    │   Modbus     │
│   RS485      │    │  Box Connect │    │  Standard    │
│   0x17       │    │  Propriétaire│    │   0x03       │
│  19200 bps   │    │  115200 bps  │    │  1200 bps    │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Tests à effectuer sur RBUV

### T01 - Détection baudrate 115200

```bash
# Fermer pac_aldes_mqtt.py d'abord !
sudo systemctl stop pac_aldes

# Test communication 115200
stty -F /dev/ttyACM1 115200 cs8 -parenb -cstopb raw -echo
timeout 30 cat /dev/ttyACM1 | xxd | head -50
```

**Attendu** : Si le RBUV supporte ce protocole, on devrait voir des trames `FA FD` (Ping).

### T02 - Envoi Pong et observation

```python
import serial
import time

ser = serial.Serial('/dev/ttyACM1', 115200, timeout=1)

# Envoyer Pong
pong = bytes([0xFD, 0xFA, 0x07, 0xFF, 0x13, 0xFE, 0xF2])
ser.write(pong)

# Attendre réponse
time.sleep(2)
response = ser.read(256)
print(response.hex(' '))
```

### T03 - Envoi initialisation

```python
# Trame d'initialisation (switch vers mode standard)
init = bytes([0x02, 0x03, 0x04, 0x20, 0x00, 0x01, 0x02, 0x42, 0xA2])
ser.write(init)
time.sleep(1)
response = ser.read(256)
print(f"Longueur: {len(response)}, Data: {response.hex(' ')}")
```

### T04 - Requête consignes

```python
# Requête type 0x21 (consignes)
req_21 = bytes([0xFD, 0xFA, 0x08, 0xFF, 0x41, 0x21, 0xFE, 0xA2])
ser.write(req_21)
time.sleep(1)
response = ser.read(256)
print(f"Type 21: {response.hex(' ')}")
```

## Référence croisée avec protocole 0x17

| Fonction | 0x17 (télécommande) | Box Connect USB |
|----------|---------------------|-----------------|
| On/Off | Offset 36-37 | Type 0x58 (à déterminer) |
| Chauffage/Clim | Offset 38-39 | Type 0x58 (à déterminer) |
| Eco/Confort | Offset 18-19 | Type 0x58 (à déterminer) |
| Consignes | Read-only | Type 0x21 lecture, 0x58 écriture ? |
| Températures | Via registres | Type 0x22 monitoring |

## Questions ouvertes

1. **Le RBUV 2018 supporte-t-il ce protocole ?**
   - Peut-être réservé aux modèles récents avec Box Connect

2. **Coexistence des protocoles ?**
   - Peut-on utiliser 115200 ET 1200 sur le même port USB ?
   - Faut-il une séquence d'initialisation spécifique ?

3. **Écriture des consignes thermostats ?**
   - Si l'écriture fonctionne via 0x58, les consignes R20-R25 seraient-elles modifiables ?

4. **Checksum exact ?**
   - `FE` + 1 octet calculé sur la somme - formule exacte à déterminer

## Historique

| Date | Événement |
|------|-----------|
| 2025-01-16 | Documentation des découvertes @djtef |
| - | Tests sur RBUV à effectuer |

---

*Document basé sur l'analyse de @djtef partagée sur le forum HACF*
