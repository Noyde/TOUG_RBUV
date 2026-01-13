# TOUG_RBUV - Intégration PAC Aldes T.One RBUV (modèles 2018)

![License](https://img.shields.io/badge/license-MIT-yellow)
![MQTT Discovery](https://img.shields.io/badge/MQTT-Discovery-purple)
![ESPHome](https://img.shields.io/badge/ESPHome-component-000000?logo=esphome)
![Status](https://img.shields.io/badge/status-beta-orange)

---

## ⚠️ AVERTISSEMENT - PROJET EN BETA

> **CE PROJET EST EN COURS DE DÉVELOPPEMENT**
>
> - 🚧 **Version BETA** - Nombreuses validations encore nécessaires
> - ⚠️ **UTILISATION À VOS RISQUES ET PÉRILS**
> - 🔬 Basé sur du reverse engineering (protocole non documenté par Aldes)
> - 🐛 Des bugs et comportements inattendus sont possibles
> - 🏠 Ne pas utiliser en production sans tests approfondis
>
> **L'auteur décline toute responsabilité en cas de dysfonctionnement de votre PAC.**

---

## 🙏 Remerciements

Ce projet est un **complément** au projet [TOUG](https://github.com/djtef/toug) créé par **@djtef**.

Un immense merci à lui pour son travail de reverse engineering sur les PAC Aldes T.One qui a servi de base à ce projet !

> **Note :** Le projet TOUG fonctionne parfaitement sur les **modèles récents** (T.One AquaAIR, modèles post-2020).  
> Ce projet TOUG_RBUV est destiné aux **anciens modèles RBUV (2018 et antérieurs)** qui nécessitent des adaptations spécifiques.

---

## 📋 Sommaire

- [Pourquoi ce projet ?](#-pourquoi-ce-projet-)
- [Différences avec TOUG](#-différences-avec-toug)
- [Matériel compatible](#-matériel-compatible)
- [Installation](#-installation)
- [Documentation technique](#-documentation-technique)
- [Statut du projet](#-statut-du-projet)

---

## ❓ Pourquoi ce projet ?

Les PAC Aldes T.One **RBUV (série 2018 et antérieures)** présentent des différences avec les modèles récents :

- **Pas de connecteur Modbus utilisateur dédié** → connexion via bus télécommande uniquement
- **Écriture Modbus bloquée** → `illegal data address` sur les registres d'écriture (USB et RS485)
- **Protocole propriétaire 0x17** → seule méthode d'écriture fonctionnelle

Ce projet documente ces spécificités et propose des solutions adaptées.

---

## 🔄 Différences avec TOUG

| Aspect | TOUG (modèles récents) | TOUG_RBUV (modèles 2018) |
|--------|------------------------|--------------------------|
| **Connecteur Modbus utilisateur** | ✅ Présent | ❌ Absent |
| **Lecture Modbus USB** | ✅ | ✅ Identique |
| **Écriture Modbus standard** | ✅ | ❌ Bloquée |
| **Protocole 0x17** | Non nécessaire | ✅ Seule méthode écriture |
| **Bus télécommande** | RS485 standard | RS485 (19200 bauds) |

---

## 🔧 Matériel compatible

### PAC testée

| Élément | Valeur |
|---------|--------|
| **Modèle** | T.One AIR 04 |
| **Référence UI** | RBC04MX |
| **Référence UE** | RBUV04F |
| **Année** | 2018 |

### Options d'intégration

| Option | Lecture | Écriture | Coût |
|--------|---------|----------|------|
| **Pi Zero USB** | ✅ | ❌ | ~28€ |
| **ESP32 RS485** | ✅ | ✅ (0x17) | ~25€ |

---

## 📦 Installation

> 🚧 **En cours de développement** - Testez avec prudence

### Option 1 : Lecture seule (Pi Zero)

Voir [docs/pi-zero-setup.md](docs/pi-zero-setup.md)

### Option 2 : Lecture + Écriture (ESP32)

Voir [esphome/README.md](esphome/README.md)

---

## 📚 Documentation technique

| Document | Description |
|----------|-------------|
| [docs/registers.md](docs/registers.md) | Mapping des 40 registres Modbus |
| [docs/protocol.md](docs/protocol.md) | Analyse du protocole 0x17 |
| [docs/hardware.md](docs/hardware.md) | Schémas de câblage |
| [docs/pi-zero-setup.md](docs/pi-zero-setup.md) | Guide Pi Zero |
| [esphome/README.md](esphome/README.md) | Guide ESPHome |
| [tests/README.md](tests/README.md) | **Matrice de tests TOUG + RBUV** |

---

## 📊 Statut du projet

| Fonctionnalité | Statut | Validé |
|----------------|--------|--------|
| Lecture registres (40) | ✅ Complété | ✅ 40/40 (2025-01-11) |
| Mapping TOUG vs RBUV | ✅ Complété | ✅ Validé par écran PAC |
| Tests écriture USB | ✅ Complété | ✅ 8/10 (échecs attendus) |
| Sniffing protocole 0x17 | ✅ Complété | ✅ X01-X20 (2025-01-13) |
| Envoi trames 0x17 (ESP32) | 🔄 En cours | ⚠️ Tests Y01-Y07 à faire |
| Intégration ESPHome | 🔄 En cours | ⚠️ À revalider |
| Écriture consignes thermostats | ❌ Impossible | ✅ Confirmé (hardware) |

### Découvertes clés (modèles sans ECS)

| Registre | TOUG (avec ECS) | RBUV (sans ECS) |
|----------|-----------------|-----------------|
| **R39** | T° extérieure | T° Zone 4 |
| **R112** | Sonde ECS bas | **T° extérieure** |
| **R117** | Échangeur capillaire | **T° sortie compresseur** |
| **R44** | T° sortie compresseur | ❌ Non implémenté |

> **Important** : Sur les modèles RBUV sans ECS, certains registres ont une fonction différente de TOUG.

### Ce qui reste à faire

Voir la [matrice de tests complète](tests/README.md) pour le détail des validations.

- [x] ~~Revalider tous les registres TOUG sur modèle RBUV~~ ✅ 2025-01-10
- [x] ~~Tests écriture Modbus standard (USB)~~ ✅ 2025-01-10
- [ ] Tests écriture Modbus standard (RS485)
- [x] ~~Sniffing télécommande (protocole 0x17)~~ ✅ 2025-01-13 (X01-X20)
- [ ] Tests envoi ESP32 (Y01-Y07)
- [ ] Tester le composant ESPHome en conditions réelles
- [ ] Valider la stabilité long terme
- [ ] Tests avec différentes versions firmware PAC

---

## ⚠️ Limitations connues

1. **Consignes thermostats NON modifiables** - Hardware read-only (pilotées par radio 868MHz)
2. **Télécommande doit être débranchée** - Collision sur le bus RS485 sinon
3. **Date/heure non transmise via 0x17** - Chaque appareil maintient sa propre horloge
4. **Protocole non officiel** - Reverse engineering, peut changer selon firmware
5. **Testé sur UN SEUL modèle** - RBUV04F 2018

---

## 🔗 Ressources

| Ressource | Lien |
|-----------|------|
| Projet TOUG (djtef) | https://github.com/djtef/toug |
| Forum HACF | https://forum.hacf.fr/t/aldes-t-one-air-aquaair/42974 |
| TOUG DefiDIY25 | https://forum.hacf.fr/t/defidiy25-toug-passerelle-esphome-pour-piloter-la-pac-aldes-t-one-sans-cloud-et-avec-routeur-solaire/68244 |
| Doc Aldes officielle | https://assets.aldes.fr/assets/docsFR/t.one-air-notice-d-installation-d-entretien-de-maintenance.pdf |

---

## 🤝 Contribuer

Ce projet est en beta. Toute aide est bienvenue :

- 🐛 Signaler des bugs
- 📝 Améliorer la documentation
- 🧪 Tester sur d'autres modèles RBUV
- 💡 Proposer des améliorations

---

*2025 - Noyde*

**⚠️ RAPPEL : Projet BETA - Utilisation à vos risques et périls**
