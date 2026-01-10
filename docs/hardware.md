# Matériel et câblage

Guide du matériel nécessaire et schémas de câblage pour l'intégration de la PAC Aldes T.One RBUV.

---

## 1. Options d'intégration

| Option | Matériel | Lecture | Écriture | Coût |
|--------|----------|---------|----------|------|
| **Pi Zero USB** | Pi Zero 2 W + câble USB | ✅ | ❌ | ~28€ |
| **ESP32 RS485** | ESP32 + RS485 + Level Shifter | ✅ | ✅ (0x17) | ~25€ |

---

## 2. Option Pi Zero (lecture seule)

### Liste des composants

| Composant | Référence | Prix approx. |
|-----------|-----------|--------------|
| Raspberry Pi Zero 2 W | - | ~18€ |
| Carte microSD | 16 Go minimum | ~5€ |
| Adaptateur USB OTG | USB-A vers Micro-USB | ~3€ |
| Câble USB | USB-A vers Mini-USB | ~2€ |
| **Total** | | **~28€** |

### Schéma de connexion
```
┌─────────────────────┐
│   PAC T.One AIR     │
│                     │
│   Port USB          │
│   (Mini-USB)        │
│   1200 bauds        │
└─────────┬───────────┘
          │
          │ Câble USB-A vers Mini-USB
          │
┌─────────┴───────────┐
│ Adaptateur OTG      │
│ USB-A → Micro-USB   │
└─────────┬───────────┘
          │
┌─────────┴───────────┐
│ Raspberry Pi Zero   │
│ 2 W                 │
│                     │
│ Port USB (milieu)   │
│ PAS le port PWR     │
└─────────────────────┘
```

> **Note** : Le Pi peut être alimenté par le port USB de la PAC. Si le courant est insuffisant, utiliser une alimentation externe sur le port PWR.

---

## 3. Option ESP32 RS485 (lecture + écriture)

### Liste des composants

| Composant | Référence | Prix approx. |
|-----------|-----------|--------------|
| ESP32 D1 Mini | WROOM-32, USB-C | ~8€ |
| Module RS485 | MAX485 | ~2€ |
| Level Shifter | BSS138 4 canaux | ~3€ |
| Step-Down | Mini360 (12V→5V) | ~2€ |
| Fils Dupont | F-F 10cm | ~2€ |
| **Total** | | **~17€** |

### Matériel optionnel (Phase 2 - détection bouches)

| Composant | Référence | Prix approx. |
|-----------|-----------|--------------|
| Optocoupler 8ch | HL-OI-VT-8-N (12V→3.3V PNP) | ~16€ |

---

## 4. Connecteur télécommande PAC

Le connecteur télécommande de la PAC fournit l'alimentation et le bus RS485 :

| Pin | Signal | Description |
|-----|--------|-------------|
| 1 | +12V | Alimentation 12V DC |
| 2 | GND | Masse commune |
| 3 | A | RS485 Data+ |
| 4 | B | RS485 Data- |

---

## 5. Description des composants ESP32

### Step-Down Mini360

Convertisseur DC-DC qui transforme le 12V de la PAC en ~4.4V pour alimenter l'ESP32 et les modules.

| Broche | Connexion |
|--------|-----------|
| IN+ | PAC +12V |
| IN- | PAC GND |
| OUT+ | ESP32 VCC, Level Shifter HV, RS485 VCC |
| OUT- | GND commun |

**Réglage** : Ajuster le potentiomètre pour obtenir ~4.4V en sortie.

### Module RS485 (MAX485)

Convertit les signaux UART de l'ESP32 en RS485 pour communiquer avec la PAC.

| Broche | Fonction | Connexion |
|--------|----------|-----------|
| VCC | Alimentation | Step-Down ~4.4V |
| GND | Masse | GND commun |
| A | RS485 Data+ | PAC A |
| B | RS485 Data- | PAC B |
| RO | Receiver Output | Level Shifter HV1 |
| DI | Driver Input | Level Shifter HV2 |
| DE | Driver Enable | GPIO4 (ponté avec RE) |
| RE | Receiver Enable | GPIO4 (ponté avec DE) |

### Level Shifter BSS138

Adapte les niveaux de tension entre le RS485 (5V) et l'ESP32 (3.3V).

| Broche | Fonction | Connexion |
|--------|----------|-----------|
| LV | Tension basse | ESP32 3.3V |
| HV | Tension haute | Step-Down ~4.4V |
| GND | Masse | GND commun |
| LV1 | Canal 1 basse tension | ESP32 GPIO16 (RX) |
| HV1 | Canal 1 haute tension | RS485 RO |
| LV2 | Canal 2 basse tension | ESP32 GPIO17 (TX) |
| HV2 | Canal 2 haute tension | RS485 DI |

### ESP32 D1 Mini

| Broche | Fonction | Connexion |
|--------|----------|-----------|
| VCC | Alimentation 5V | Step-Down ~4.4V |
| GND | Masse | GND commun |
| 3.3V | Sortie régulée | Level Shifter LV |
| GPIO16 | UART RX | Level Shifter LV1 |
| GPIO17 | UART TX | Level Shifter LV2 |
| GPIO4 | Flow Control | RS485 DE + RE |

---

## 6. Tableau récapitulatif des connexions

| De | Vers | Couleur suggérée |
|----|------|------------------|
| PAC +12V | Step-Down IN+ | Rouge |
| PAC GND | Step-Down IN- | Noir |
| PAC A | RS485 A | Jaune |
| PAC B | RS485 B | Orange |
| Step-Down OUT+ | ESP32 VCC | Vert |
| Step-Down OUT+ | Level Shifter HV | Vert |
| Step-Down OUT+ | RS485 VCC | Vert |
| Step-Down GND | GND commun | Noir |
| RS485 RO | Level Shifter HV1 | Bleu |
| RS485 DI | Level Shifter HV2 | Violet |
| RS485 DE | GPIO4 | Rose |
| RS485 RE | GPIO4 (ponté) | Rose |
| Level Shifter LV | ESP32 3.3V | Cyan |
| Level Shifter LV1 | ESP32 GPIO16 | Bleu |
| Level Shifter LV2 | ESP32 GPIO17 | Violet |
| Level Shifter GND | GND commun | Noir |

---

## 7. Schéma ASCII
```
                    ┌────────────────────────────────────────────────┐
                    │              PAC T.One AIR                     │
                    │         Connecteur TÉLÉCOMMANDE                │
                    │  ┌──────┬──────┬──────┬──────┐                 │
                    │  │ +12V │ GND  │  A   │  B   │                 │
                    │  └──┬───┴──┬───┴──┬───┴──┬───┘                 │
                    └─────┼──────┼──────┼──────┼─────────────────────┘
                          │      │      │      │
            Rouge ────────┘      │      │      │
            Noir ────────────────┘      │      │
            Jaune ──────────────────────┘      │
            Orange ────────────────────────────┘
                          │      │      │      │
                    ┌─────┴──────┴──────┴──────┴─────┐
                    │       STEP-DOWN Mini360        │
                    │  IN+  IN-         OUT+  OUT-   │
                    └───────────────────┬─────┬──────┘
                                        │     │
                        Vert (4.4V) ────┘     └──── Noir (GND)
                              │                      │
          ┌───────────────────┼──────────────────────┼────────────────┐
          │                   │                      │                │
    ┌─────┴─────┐      ┌──────┴──────┐        ┌──────┴──────┐         │
    │  RS485    │      │Level Shifter│        │   ESP32     │         │
    │  MAX485   │      │   BSS138    │        │  D1 Mini    │         │
    │           │      │             │        │             │         │
    │ VCC ──────┼──────┤ HV          │        │ VCC ────────┤         │
    │ GND ──────┼──────┼─────────────┼────────┤ GND ────────┼─────────┤
    │           │      │ LV ─────────┼────────┤ 3.3V        │         │
    │ A ────────┼── Jaune (vers PAC) │        │             │         │
    │ B ────────┼── Orange (vers PAC)│        │             │         │
    │ RO ───────┼──────┤ HV1    LV1  ├────────┤ GPIO16 (RX) │         │
    │ DI ───────┼──────┤ HV2    LV2  ├────────┤ GPIO17 (TX) │         │
    │ DE ───────┼──────┼─────────────┼────────┤ GPIO4       │         │
    │ RE ───────┼──┘   │             │        │             │         │
    └───────────┘      └─────────────┘        └─────────────┘         │
                                                                      │
                                              GND COMMUN ─────────────┘
```

---

## 8. Flux des données

### Réception (PAC → ESP32)
```
PAC → RS485 (A/B) → MAX485 (RO) → Level Shifter (HV1→LV1) → ESP32 (GPIO16)
```

### Émission (ESP32 → PAC)
```
ESP32 (GPIO17) → Level Shifter (LV2→HV2) → MAX485 (DI) → RS485 (A/B) → PAC
```

---

## 9. Procédure de câblage

### Étapes

1. **COUPER LE DISJONCTEUR PAC** - Sécurité obligatoire
2. Câbler le Step-Down (entrée 12V depuis PAC)
3. Régler le Step-Down à ~4.4V avec un multimètre
4. Câbler le Level Shifter (LV vers 3.3V ESP32, HV vers Step-Down)
5. Câbler le RS485 (A/B vers PAC, RO/DI vers Level Shifter)
6. Connecter DE et RE ensemble vers GPIO4
7. **DÉBRANCHER LA TÉLÉCOMMANDE** - Évite les collisions
8. Remettre le disjoncteur
9. Vérifier que l'ESP32 s'allume
10. Vérifier les logs ESPHome

### Points de vérification

| Vérification | Méthode | Valeur attendue |
|--------------|---------|-----------------|
| Tension Step-Down | Multimètre | ~4.4V |
| ESP32 alimenté | LED visible | Allumée |
| Communication | Logs ESPHome | Valeurs Modbus |

---

## 10. Dépannage matériel

| Problème | Cause probable | Solution |
|----------|----------------|----------|
| ESP32 ne démarre pas | Tension insuffisante | Vérifier Step-Down (~4.4V) |
| Erreurs CRC massives | Télécommande branchée | Débrancher télécommande |
| Valeurs corrompues | Level Shifter absent | Ajouter BSS138 |
| Pas de réponse Modbus | A/B inversés | Inverser fils A et B |
| Communication intermittente | Mauvaise masse | Vérifier GND commun |

---

## 11. Ressources

| Ressource | Lien |
|-----------|------|
| Projet TOUG (djtef) | https://github.com/djtef/toug |
| Schéma électrique Aldes | https://assets.aldes.fr/assets/docsFR/t.one-air-schema-electrique-notice-d-installation.pdf |
| ESPHome Modbus | https://esphome.io/components/modbus_controller.html |

---

*Documentation TOUG_RBUV - Matériel et câblage*
