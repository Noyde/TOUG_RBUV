# TOUG_RBUV - Intégration PAC Aldes T.One RBUV (modèles 2018)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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
- **Écriture USB bloquée** → `illegal data address` sur les registres d'écriture
- **Protocole différent** pour certaines commandes

Ce projet documente ces spécificités et propose des solutions adaptées.

---

## 🔄 Différences avec TOUG

| Aspect | TOUG (modèles récents) | TOUG_RBUV (modèles 2018) |
|--------|------------------------|--------------------------|
| **Connecteur Modbus utilisateur** | ✅ Présent | ❌ Absent |
| **Écriture via USB** | ✅ Fonctionne | ❌ Bloqué |
| **Lecture Modbus USB** | ✅ | ✅ Identique |
| **Bus télécommande** | RS485 standard | RS485 (seule option écriture) |

---

## 🔧 Matériel compatible

### PAC testée

| Élément | Valeur |
|---------|--------|
| **Modèle** | T.One AIR 04 |
| **Référence UI** | RBC04MX |
| **Référence UE** | RBUV04F |
| **Année** | 2018 |
| **Fluide** | R410a (1.5 kg) |

### Matériel d'intégration

- **Option 1** : Raspberry Pi Zero 2 W + adaptateur USB-RS485 (lecture seule)
- **Option 2** : ESP32 + module RS485 MAX485 (TOUG standard)

---

## 📦 Installation

> 🚧 **En cours de développement** - Documentation complète à venir

### Lecture seule (Pi Zero)

Voir [docs/pi-zero-setup.md](docs/pi-zero-setup.md)

### Intégration ESPHome

Voir [docs/esphome-setup.md](docs/esphome-setup.md)

---

## 📚 Documentation technique

| Document | Description |
|----------|-------------|
| [docs/registers.md](docs/registers.md) | Mapping des registres Modbus |
| [docs/protocol.md](docs/protocol.md) | Analyse du protocole |
| [docs/hardware.md](docs/hardware.md) | Schémas de câblage |

---

## 📊 Statut du projet

| Fonctionnalité | Statut |
|----------------|--------|
| Lecture registres (34) | 🔄 En cours |
| Dashboard Home Assistant | 🔄 En cours |
| Écriture mode PAC | 🔄 En cours (bus télécommande) |
| Écriture consignes | 🔄 En cours |
| Intégration ESPHome | 🔄 En cours |

---

## 🔗 Ressources

| Ressource | Lien |
|-----------|------|
| Projet TOUG (djtef) | https://github.com/djtef/toug |
| Forum HACF | https://forum.hacf.fr/t/aldes-t-one-air-aquaair/42974 |
| TOUG DefiDIY25 | https://forum.hacf.fr/t/defidiy25-toug-passerelle-esphome-pour-piloter-la-pac-aldes-t-one-sans-cloud-et-avec-routeur-solaire/68244 |
| Doc Aldes officielle | https://assets.aldes.fr/assets/docsFR/t.one-air-notice-d-installation-d-entretien-de-maintenance.pdf |

---

*2025 - Noyde*
