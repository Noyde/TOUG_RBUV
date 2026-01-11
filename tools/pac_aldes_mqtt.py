#!/usr/bin/env python3
"""
PAC Aldes T.One AIR - Lecteur Modbus USB vers MQTT
Pour Raspberry Pi Zero W

Projet TOUG_RBUV - Complément au projet TOUG de @djtef
https://github.com/djtef/toug

Version: 4.1
Licence: MIT

Communication USB: 1200 bauds, 8 bits, parité EVEN, 1 stop bit

NOTE: Ce script permet uniquement la LECTURE des registres.
L'écriture n'est pas possible via USB sur les modèles RBUV 2018.

CHANGELOG v4.1:
- 40 registres (R16/R17 retirés - non fonctionnels sur RBUV)
- R16/R17 (Date/Heure) ne sont pas accessibles via USB sur RBUV

CHANGELOG v4.0:
- 42 registres complets (tous testés USB 2025-01-10)
- Ajout R14-R15 (Panel ID)
- Ajout R49 (Courant compresseur), R51 (Protection)
- Ajout R72-R73 (Temps ON compresseur 32-bit)
"""

import time
import json
import logging
import serial
import paho.mqtt.client as mqtt

# =============================================================================
# CONFIGURATION - À ADAPTER À VOTRE INSTALLATION
# =============================================================================

# MQTT
MQTT_BROKER = "192.168.1.100"   # IP de votre broker MQTT
MQTT_PORT = 1883
MQTT_USER = ""                   # Laisser vide si pas d'authentification
MQTT_PASSWORD = ""               # Laisser vide si pas d'authentification
MQTT_BASE_TOPIC = "homeassistant"
MQTT_STATE_TOPIC = "pac_aldes"

# Modbus USB
SERIAL_PORT = "/dev/ttyACM1"     # Port USB de la PAC (vérifier avec dmesg)
BAUDRATE = 1200                  # Bus USB = 1200 bauds (NE PAS MODIFIER)
MODBUS_ADDRESS = 0x01

# Intervalle de lecture (secondes)
READ_INTERVAL = 30

# =============================================================================
# REGISTRES MODBUS - 40 registres (R16/R17 retirés - non fonctionnels RBUV)
# Adaptez les noms de zones à votre installation
# =============================================================================

REGISTERS = {
    # =========================================================================
    # SYSTÈME (6 registres) - R16/R17 retirés (Date/Heure non accessibles USB)
    # =========================================================================
    "version": {"address": 1, "name": "Version Firmware", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:information-outline"},
    "duree_on": {"address": 3, "name": "Durée ON", "unit": "min", "divisor": 1, "device_class": "duration", "icon": "mdi:clock-outline"},
    "mode": {"address": 9, "name": "Mode PAC", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:hvac"},
    "panel_id_bas": {"address": 14, "name": "Panel ID (bas)", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:identifier"},
    "panel_id_haut": {"address": 15, "name": "Panel ID (haut)", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:identifier"},
    "protection_compresseur": {"address": 51, "name": "Protection Compresseur", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:shield"},

    # =========================================================================
    # THERMOSTATS - CONSIGNES (R20-R25) - 6 zones
    # Note: Adaptez les noms à vos pièces
    # =========================================================================
    "consigne_zone1": {"address": 20, "name": "Consigne Zone 1", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer"},
    "consigne_zone1_bis": {"address": 21, "name": "Consigne Zone 1 bis", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer"},
    "consigne_zone2": {"address": 22, "name": "Consigne Zone 2", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer"},
    "consigne_zone3": {"address": 23, "name": "Consigne Zone 3", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer"},
    "consigne_zone4": {"address": 24, "name": "Consigne Zone 4", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer"},
    "consigne_zone5": {"address": 25, "name": "Consigne Zone 5", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer"},

    # =========================================================================
    # THERMOSTATS - TEMPÉRATURES (R36-R41) - 6 zones
    # =========================================================================
    "temp_zone1": {"address": 36, "name": "Température Zone 1", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
    "temp_zone2": {"address": 37, "name": "Température Zone 2", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
    "temp_zone3": {"address": 38, "name": "Température Zone 3", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
    "temp_zone4": {"address": 39, "name": "Température Zone 4", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
    "temp_zone5": {"address": 40, "name": "Température Zone 5", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
    "temp_zone6": {"address": 41, "name": "Température Zone 6", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},

    # =========================================================================
    # VENTILATION (4 registres)
    # =========================================================================
    "consigne_ventilateur": {"address": 60, "name": "Consigne Ventilateur", "unit": "rpm", "divisor": 1, "device_class": None, "icon": "mdi:fan"},
    "vitesse_ventilateur": {"address": 61, "name": "Vitesse Ventilateur", "unit": "rpm", "divisor": 1, "device_class": None, "icon": "mdi:fan"},
    "niveau_ventil_ue": {"address": 106, "name": "Niveau Ventilation UE", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:fan-speed-1"},
    "heures_ventilateur": {"address": 125, "name": "Heures Ventilateur UI", "unit": "h", "divisor": 1, "device_class": "duration", "icon": "mdi:clock-outline"},

    # =========================================================================
    # COMPRESSEUR (7 registres)
    # =========================================================================
    "courant_compresseur": {"address": 49, "name": "Courant Compresseur", "unit": "A", "divisor": 100, "device_class": "current", "icon": "mdi:current-ac"},
    "consigne_freq_compresseur": {"address": 65, "name": "Consigne Fréquence Compresseur", "unit": "Hz", "divisor": 10, "device_class": "frequency", "icon": "mdi:sine-wave"},
    "freq_compresseur": {"address": 66, "name": "Fréquence Compresseur", "unit": "Hz", "divisor": 10, "device_class": "frequency", "icon": "mdi:sine-wave"},
    "temps_on_compresseur_bas": {"address": 72, "name": "Temps ON Compresseur (bas)", "unit": "s", "divisor": 1, "device_class": None, "icon": "mdi:timer"},
    "temps_on_compresseur_haut": {"address": 73, "name": "Temps ON Compresseur (haut)", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:timer"},
    "heures_compresseur": {"address": 127, "name": "Heures Compresseur", "unit": "h", "divisor": 1, "device_class": "duration", "icon": "mdi:clock-outline"},

    # =========================================================================
    # TEMPÉRATURES PAC INTERNES (5 registres)
    # =========================================================================
    "temp_air_repris": {"address": 111, "name": "Température Air Repris UI", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
    "temp_exterieure": {"address": 112, "name": "Température Extérieure", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
    "temp_echangeur_ui": {"address": 114, "name": "Température Échangeur UI", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
    "temp_echangeur_ue": {"address": 115, "name": "Température Échangeur UE", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
    "temp_sortie_compresseur": {"address": 117, "name": "Température Sortie Compresseur", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": False},

    # =========================================================================
    # VANNES EEV (Détendeurs électroniques) - 2 registres
    # =========================================================================
    "eev1": {"address": 104, "name": "EEV1", "unit": "Pls", "divisor": 1, "device_class": None, "icon": "mdi:valve"},
    "eev2": {"address": 105, "name": "EEV2", "unit": "Pls", "divisor": 1, "device_class": None, "icon": "mdi:valve"},

    # =========================================================================
    # DÉBITS / PRESSIONS (5 registres)
    # =========================================================================
    "pse_debit_nominal": {"address": 247, "name": "PSE Débit Nominal", "unit": "Pa", "divisor": 1, "device_class": "pressure", "icon": "mdi:gauge"},
    "pse_debit_mini": {"address": 248, "name": "PSE Débit Mini", "unit": "Pa", "divisor": 1, "device_class": "pressure", "icon": "mdi:gauge"},
    "debit_1_bouche": {"address": 249, "name": "Débit 1 Bouche", "unit": "m³/h", "divisor": 1, "device_class": None, "icon": "mdi:weather-windy"},
    "debit_nominal": {"address": 250, "name": "Débit Nominal", "unit": "m³/h", "divisor": 1, "device_class": None, "icon": "mdi:weather-windy"},
    "pression_statique_ext": {"address": 251, "name": "Pression Statique Ext", "unit": "Pa", "divisor": 1, "device_class": "pressure", "icon": "mdi:gauge"},
}

# Modes PAC (valeurs du registre 9)
MODE_PAC = {
    2: "Rafraîchissement",
    4: "Chauffage",
    5: "Off"
}

# =============================================================================
# FONCTIONS MODBUS
# =============================================================================

def calculate_crc(data):
    """Calcul CRC16 Modbus"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def read_holding_register(ser, address, register):
    """Lire un registre Modbus"""
    request = bytes([address, 0x03, (register >> 8) & 0xFF, register & 0xFF, 0x00, 0x01])
    crc = calculate_crc(request)
    request += bytes([crc & 0xFF, (crc >> 8) & 0xFF])

    ser.reset_input_buffer()
    ser.write(request)
    time.sleep(0.15)

    response = ser.read(7)
    if len(response) == 7 and response[1] == 0x03:
        return (response[3] << 8) | response[4]
    return None

def read_all_registers(ser):
    """Lire tous les registres configurés"""
    values = {}
    success_count = 0

    for key, reg in REGISTERS.items():
        try:
            raw = read_holding_register(ser, MODBUS_ADDRESS, reg["address"])
            if raw is not None:
                # Gestion des valeurs signées (températures négatives)
                if reg.get("signed", False) and raw > 32767:
                    raw = raw - 65536

                value = raw / reg["divisor"]
                values[key] = value
                success_count += 1
            else:
                values[key] = None
        except Exception as e:
            logging.warning(f"Erreur lecture {key}: {e}")
            values[key] = None

        time.sleep(0.05)

    logging.info(f"Lecture terminée: {success_count}/{len(REGISTERS)} registres OK")
    return values

# =============================================================================
# FONCTIONS MQTT
# =============================================================================

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("✅ Connecté au broker MQTT")
    else:
        logging.error(f"❌ Erreur connexion MQTT: {rc}")

def publish_discovery(mqtt_client):
    """Publier la configuration MQTT Discovery pour Home Assistant"""
    device_info = {
        "identifiers": ["pac_aldes_tone_air"],
        "name": "PAC Aldes T.One AIR",
        "manufacturer": "Aldes",
        "model": "T.One AIR RBUV",
        "sw_version": "TOUG_RBUV 4.1"
    }

    for key, reg in REGISTERS.items():
        config = {
            "name": reg["name"],
            "unique_id": f"pac_aldes_{key}",
            "state_topic": f"{MQTT_STATE_TOPIC}/state",
            "value_template": f"{{{{ value_json.{key} }}}}",
            "device": device_info,
            "icon": reg.get("icon", "mdi:information"),
        }

        if reg["unit"]:
            config["unit_of_measurement"] = reg["unit"]
        if reg.get("device_class"):
            config["device_class"] = reg["device_class"]
            config["state_class"] = "measurement"

        topic = f"{MQTT_BASE_TOPIC}/sensor/pac_aldes_{key}/config"
        mqtt_client.publish(topic, json.dumps(config), retain=True)

    logging.info(f"📢 MQTT Discovery publié ({len(REGISTERS)} entités)")

def publish_values(mqtt_client, values):
    """Publier les valeurs sur MQTT"""
    # Convertir le mode en texte
    if "mode" in values and values["mode"] is not None:
        mode_code = int(values["mode"])
        values["mode_text"] = MODE_PAC.get(mode_code, f"Inconnu ({mode_code})")

    # Filtrer les None
    filtered = {k: v for k, v in values.items() if v is not None}

    mqtt_client.publish(f"{MQTT_STATE_TOPIC}/state", json.dumps(filtered))
    logging.info(f"📤 Valeurs publiées sur MQTT ({len(filtered)}/{len(values)} registres)")

def print_status(values):
    """Afficher un résumé dans les logs"""
    if values.get("mode") is not None:
        mode = MODE_PAC.get(int(values["mode"]), "Inconnu")
        logging.info(f"  Mode PAC: {mode}")
    if values.get("temp_exterieure") is not None:
        logging.info(f"  T° Extérieure: {values['temp_exterieure']:.1f}°C")
    if values.get("freq_compresseur") is not None:
        logging.info(f"  Fréquence Compresseur: {values['freq_compresseur']:.1f} Hz")
    if values.get("courant_compresseur") is not None:
        logging.info(f"  Courant Compresseur: {values['courant_compresseur']:.2f} A")

# =============================================================================
# MAIN
# =============================================================================

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     TOUG_RBUV - Aldes T.One AIR Modbus Reader v4.1           ║
║     Raspberry Pi USB → MQTT → Home Assistant                 ║
║     40 registres (R16/R17 retirés - non fonctionnels RBUV)   ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Connexion MQTT
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "pac_aldes_reader")
    mqtt_client.on_connect = on_connect

    if MQTT_USER:
        mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        logging.error(f"❌ Erreur connexion MQTT: {e}")
        return

    time.sleep(2)
    publish_discovery(mqtt_client)

    # Connexion série
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        logging.info(f"✅ Port série ouvert: {SERIAL_PORT} @ {BAUDRATE} bauds")
    except Exception as e:
        logging.error(f"❌ Erreur ouverture port série: {e}")
        return

    logging.info(f"🔄 Lecture toutes les {READ_INTERVAL} secondes...")

    try:
        while True:
            values = read_all_registers(ser)
            publish_values(mqtt_client, values)
            print_status(values)
            time.sleep(READ_INTERVAL)

    except KeyboardInterrupt:
        logging.info("⏹️  Arrêt demandé")
    finally:
        ser.close()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logging.info("👋 Connexions fermées")

if __name__ == "__main__":
    main()
