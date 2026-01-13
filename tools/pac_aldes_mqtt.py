#!/usr/bin/env python3
"""
PAC Aldes T.One AIR RBUV - Modbus Reader → MQTT
TOUG_RBUV v4.3 - 41 entités (40 registres + Mode PAC Texte)

Configuration via config.json (copier config_example.json)
"""

import json
import logging
import time
import os
import sys
import glob
import serial
import paho.mqtt.client as mqtt

# =============================================================================
# CHARGEMENT CONFIGURATION
# =============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

def load_config():
    """Charger la configuration depuis config.json"""
    if not os.path.exists(CONFIG_FILE):
        print(f"❌ Fichier config.json non trouvé!")
        print(f"   Copiez config_example.json vers config.json et configurez vos valeurs.")
        print(f"   cp {SCRIPT_DIR}/config_example.json {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

CONFIG = load_config()

# Extraction config
MQTT_BROKER = CONFIG["mqtt"]["broker"]
MQTT_PORT = CONFIG["mqtt"].get("port", 1883)
MQTT_USER = CONFIG["mqtt"]["user"]
MQTT_PASSWORD = CONFIG["mqtt"]["password"]

SERIAL_PORT_CONFIG = CONFIG["serial"].get("port", "auto")
SERIAL_BAUDRATE = CONFIG["serial"]["baudrate"]

def detect_serial_port():
    """Détecte automatiquement le port série de la PAC Aldes"""
    # Si port spécifié et existe, l'utiliser
    if SERIAL_PORT_CONFIG and SERIAL_PORT_CONFIG != "auto":
        if os.path.exists(SERIAL_PORT_CONFIG):
            return SERIAL_PORT_CONFIG
        logging.warning(f"⚠️ Port configuré {SERIAL_PORT_CONFIG} non trouvé, recherche auto...")

    # Rechercher les ports ttyACM* (USB CDC)
    ports = sorted(glob.glob('/dev/ttyACM*'))
    if not ports:
        logging.error("❌ Aucun port /dev/ttyACM* trouvé")
        return None

    logging.info(f"🔍 Ports détectés: {', '.join(ports)}")

    # Tester chaque port
    for port in ports:
        try:
            logging.info(f"🔍 Test {port}...")
            ser = serial.Serial(
                port=port,
                baudrate=SERIAL_BAUDRATE,
                parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )

            # Tenter lecture registre 1 (version firmware)
            request = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01])
            crc = 0xFFFF
            for b in request:
                crc ^= b
                for _ in range(8):
                    crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
            request += bytes([crc & 0xFF, crc >> 8])

            ser.reset_input_buffer()
            ser.write(request)
            time.sleep(0.2)
            response = ser.read(7)
            ser.close()

            if len(response) >= 5 and response[0] == 0x01 and response[1] == 0x03:
                version = (response[3] << 8) | response[4]
                if 1000 <= version <= 9999:  # Versions firmware valides
                    logging.info(f"✅ PAC détectée sur {port} (firmware {version})")
                    return port
        except Exception as e:
            logging.debug(f"   {port}: {e}")
            continue

    # Si aucun port validé, utiliser le premier disponible
    logging.warning(f"⚠️ Aucun port validé, utilisation de {ports[0]}")
    return ports[0]

SERIAL_PORT = detect_serial_port()

READ_INTERVAL = CONFIG.get("read_interval", 30)

ZONES = CONFIG["zones"]

MODBUS_ADDRESS = 0x01
MQTT_BASE_TOPIC = "homeassistant"
MQTT_STATE_TOPIC = "pac_aldes"

# =============================================================================
# REGISTRES MODBUS (40 registres)
# =============================================================================

def build_registers():
    """Construire le dictionnaire des registres avec les noms de zones"""
    return {
        # SYSTÈME (6 registres)
        "version": {"address": 1, "name": "Version Firmware", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:information"},
        "duree_on": {"address": 3, "name": "Durée ON", "unit": "min", "divisor": 1, "device_class": "duration", "icon": "mdi:timer"},
        "mode": {"address": 9, "name": "Mode PAC", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:hvac"},
        "panel_id_bas": {"address": 14, "name": "Panel ID (bas)", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:identifier"},
        "panel_id_haut": {"address": 15, "name": "Panel ID (haut)", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:identifier"},
        "protection_compresseur": {"address": 51, "name": "Protection Compresseur", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:shield"},

        # CONSIGNES THERMOSTATS (6 registres) - Mapping RBUV
        # R20/R21 = même thermostat (Zone 1), R22=Zone2, R23=Zone3, R24=Zone4, R25=Zone5
        "consigne_zone1": {"address": 20, "name": f"Consigne {ZONES['zone1']}", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer"},
        "consigne_zone1bis": {"address": 21, "name": f"Consigne {ZONES['zone1']} bis", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer"},
        "consigne_zone2": {"address": 22, "name": f"Consigne {ZONES['zone2']}", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer"},
        "consigne_zone3": {"address": 23, "name": f"Consigne {ZONES['zone3']}", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer"},
        "consigne_zone4": {"address": 24, "name": f"Consigne {ZONES['zone4']}", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer"},
        "consigne_zone5": {"address": 25, "name": f"Consigne {ZONES['zone5']}", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer"},

        # TEMPÉRATURES ZONES (6 registres) - Mapping RBUV
        "temp_zone1": {"address": 36, "name": f"Température {ZONES['zone1']}", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:home-thermometer", "signed": True},
        "temp_zone1bis": {"address": 37, "name": f"Température {ZONES['zone1']} bis", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
        "temp_zone2": {"address": 38, "name": f"Température {ZONES['zone2']}", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:bed", "signed": True},
        "temp_zone3": {"address": 39, "name": f"Température {ZONES['zone3']}", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:desk", "signed": True},
        "temp_zone4": {"address": 40, "name": f"Température {ZONES['zone4']}", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
        "temp_zone5": {"address": 41, "name": f"Température {ZONES['zone5']}", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},

        # COMPRESSEUR (6 registres)
        "courant_compresseur": {"address": 49, "name": "Courant Compresseur", "unit": "A", "divisor": 100, "device_class": "current", "icon": "mdi:current-ac"},
        "consigne_freq": {"address": 65, "name": "Consigne Fréquence", "unit": "Hz", "divisor": 10, "device_class": "frequency", "icon": "mdi:sine-wave"},
        "freq_compresseur": {"address": 66, "name": "Fréquence Compresseur", "unit": "Hz", "divisor": 10, "device_class": "frequency", "icon": "mdi:sine-wave"},
        "temps_on_compresseur_bas": {"address": 72, "name": "Temps ON Compresseur (bas)", "unit": "s", "divisor": 1, "device_class": None, "icon": "mdi:timer"},
        "temps_on_compresseur_haut": {"address": 73, "name": "Temps ON Compresseur (haut)", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:timer"},
        "heures_compresseur": {"address": 127, "name": "Heures Compresseur", "unit": "h", "divisor": 1, "device_class": "duration", "icon": "mdi:counter"},

        # VENTILATION (4 registres)
        "consigne_ventilateur": {"address": 60, "name": "Consigne Ventilateur", "unit": "rpm", "divisor": 1, "device_class": None, "icon": "mdi:fan"},
        "vitesse_ventilateur": {"address": 61, "name": "Vitesse Ventilateur", "unit": "rpm", "divisor": 1, "device_class": None, "icon": "mdi:fan"},
        "niveau_ventilation_ue": {"address": 106, "name": "Niveau Ventilation UE", "unit": "", "divisor": 1, "device_class": None, "icon": "mdi:fan-speed-1"},
        "heures_ventilateur": {"address": 125, "name": "Heures Ventilateur", "unit": "h", "divisor": 1, "device_class": "duration", "icon": "mdi:counter"},

        # EEV (2 registres)
        "eev1": {"address": 104, "name": "EEV1", "unit": "Pls", "divisor": 1, "device_class": None, "icon": "mdi:valve"},
        "eev2": {"address": 105, "name": "EEV2", "unit": "Pls", "divisor": 1, "device_class": None, "icon": "mdi:valve"},

        # TEMPÉRATURES PAC (5 registres)
        "temp_air_repris": {"address": 111, "name": "Température Air Repris", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
        "temp_exterieure": {"address": 112, "name": "Température Extérieure", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:sun-thermometer", "signed": True},
        "temp_echangeur_ui": {"address": 114, "name": "Température Échangeur UI", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
        "temp_echangeur_ue": {"address": 115, "name": "Température Échangeur UE", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer", "signed": True},
        "temp_sortie_compresseur": {"address": 117, "name": "Température Sortie Compresseur", "unit": "°C", "divisor": 100, "device_class": "temperature", "icon": "mdi:thermometer-alert"},

        # DÉBITS/PRESSIONS (5 registres)
        "pse_debit_nominal": {"address": 247, "name": "PSE Débit Nominal", "unit": "Pa", "divisor": 1, "device_class": "pressure", "icon": "mdi:gauge"},
        "pse_debit_mini": {"address": 248, "name": "PSE Débit Mini", "unit": "Pa", "divisor": 1, "device_class": "pressure", "icon": "mdi:gauge"},
        "debit_1_bouche": {"address": 249, "name": "Débit 1 Bouche", "unit": "m³/h", "divisor": 1, "device_class": None, "icon": "mdi:air-filter"},
        "debit_nominal": {"address": 250, "name": "Débit Nominal", "unit": "m³/h", "divisor": 1, "device_class": None, "icon": "mdi:air-filter"},
        "pression_statique_ext": {"address": 251, "name": "Pression Statique Ext", "unit": "Pa", "divisor": 1, "device_class": "pressure", "icon": "mdi:gauge"},
    }

REGISTERS = build_registers()

# Modes PAC
MODE_PAC = {
    2: "Rafraîchissement",
    4: "Chauffage",
    5: "Off"
}

# =============================================================================
# FONCTIONS MODBUS
# =============================================================================

def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def read_register(ser, address):
    request = bytes([MODBUS_ADDRESS, 0x03, address >> 8, address & 0xFF, 0x00, 0x01])
    crc = calculate_crc(request)
    request += bytes([crc & 0xFF, crc >> 8])

    ser.write(request)
    time.sleep(0.15)

    response = ser.read(7)
    if len(response) >= 5:
        return (response[3] << 8) | response[4]
    return None

def read_all_registers(ser):
    values = {}
    for key, reg in REGISTERS.items():
        try:
            raw = read_register(ser, reg["address"])
            if raw is not None:
                if reg.get("signed") and raw > 32767:
                    raw -= 65536
                values[key] = raw / reg["divisor"]
            else:
                values[key] = None
        except Exception as e:
            logging.warning(f"Erreur lecture {key}: {e}")
            values[key] = None
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
    device_info = {
        "identifiers": ["pac_aldes_tone_air"],
        "name": "PAC Aldes T.One AIR",
        "manufacturer": "Aldes",
        "model": "T.One AIR RBUV",
        "sw_version": "TOUG_RBUV 4.3"
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

    # Capteur mode_text
    mode_text_config = {
        "name": "Mode PAC (Texte)",
        "unique_id": "pac_aldes_mode_text",
        "state_topic": f"{MQTT_STATE_TOPIC}/state",
        "value_template": "{{ value_json.mode_text }}",
        "device": device_info,
        "icon": "mdi:hvac",
    }
    mqtt_client.publish(f"{MQTT_BASE_TOPIC}/sensor/pac_aldes_mode_text/config", json.dumps(mode_text_config), retain=True)

    logging.info(f"📢 MQTT Discovery publié (41 entités)")

def publish_values(mqtt_client, values):
    if "mode" in values and values["mode"] is not None:
        mode_code = int(values["mode"])
        values["mode_text"] = MODE_PAC.get(mode_code, f"Inconnu ({mode_code})")

    filtered = {k: v for k, v in values.items() if v is not None}
    mqtt_client.publish(f"{MQTT_STATE_TOPIC}/state", json.dumps(filtered))
    logging.info(f"📤 Valeurs publiées ({len(filtered)} registres)")

def print_status(values):
    """Afficher toutes les entités dans le journal"""

    # SYSTÈME
    logging.info("═══ SYSTÈME ═══")
    if values.get("version") is not None:
        logging.info(f"  Version Firmware: {int(values['version'])}")
    if values.get("mode") is not None:
        mode = MODE_PAC.get(int(values["mode"]), f"Inconnu ({int(values['mode'])})")
        logging.info(f"  Mode PAC: {mode}")
    if values.get("duree_on") is not None:
        logging.info(f"  Durée ON: {int(values['duree_on'])} min")
    if values.get("protection_compresseur") is not None:
        logging.info(f"  Protection Compresseur: {int(values['protection_compresseur'])}")

    # CONSIGNES
    logging.info("═══ CONSIGNES ═══")
    for key in ["consigne_zone1", "consigne_zone1bis", "consigne_zone2", "consigne_zone3", "consigne_zone4", "consigne_zone5"]:
        if values.get(key) is not None:
            name = REGISTERS[key]["name"]
            logging.info(f"  {name}: {values[key]:.1f}°C")

    # TEMPÉRATURES ZONES
    logging.info("═══ TEMPÉRATURES ZONES ═══")
    for key in ["temp_zone1", "temp_zone1bis", "temp_zone2", "temp_zone3", "temp_zone4", "temp_zone5"]:
        if values.get(key) is not None:
            name = REGISTERS[key]["name"]
            logging.info(f"  {name}: {values[key]:.1f}°C")

    # TEMPÉRATURES PAC
    logging.info("═══ TEMPÉRATURES PAC ═══")
    for key in ["temp_exterieure", "temp_air_repris", "temp_echangeur_ui", "temp_echangeur_ue", "temp_sortie_compresseur"]:
        if values.get(key) is not None:
            name = REGISTERS[key]["name"]
            logging.info(f"  {name}: {values[key]:.1f}°C")

    # COMPRESSEUR
    logging.info("═══ COMPRESSEUR ═══")
    if values.get("freq_compresseur") is not None:
        logging.info(f"  Fréquence: {values['freq_compresseur']:.1f} Hz")
    if values.get("consigne_freq") is not None:
        logging.info(f"  Consigne Fréquence: {values['consigne_freq']:.1f} Hz")
    if values.get("courant_compresseur") is not None:
        logging.info(f"  Courant: {values['courant_compresseur']:.2f} A")
    if values.get("heures_compresseur") is not None:
        logging.info(f"  Heures: {int(values['heures_compresseur'])} h")

    # VENTILATION
    logging.info("═══ VENTILATION ═══")
    if values.get("vitesse_ventilateur") is not None:
        logging.info(f"  Vitesse: {int(values['vitesse_ventilateur'])} rpm")
    if values.get("consigne_ventilateur") is not None:
        logging.info(f"  Consigne: {int(values['consigne_ventilateur'])} rpm")
    if values.get("heures_ventilateur") is not None:
        logging.info(f"  Heures: {int(values['heures_ventilateur'])} h")

    # EEV
    logging.info("═══ EEV ═══")
    if values.get("eev1") is not None:
        logging.info(f"  EEV1: {int(values['eev1'])} Pls")
    if values.get("eev2") is not None:
        logging.info(f"  EEV2: {int(values['eev2'])} Pls")

    # DÉBITS/PRESSIONS
    logging.info("═══ DÉBITS/PRESSIONS ═══")
    if values.get("debit_nominal") is not None:
        logging.info(f"  Débit Nominal: {int(values['debit_nominal'])} m³/h")
    if values.get("pression_statique_ext") is not None:
        logging.info(f"  Pression Statique: {int(values['pression_statique_ext'])} Pa")

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
║     PAC Aldes T.One AIR - TOUG_RBUV v4.3                     ║
║     Raspberry Pi Zero → MQTT → Home Assistant                ║
║     41 entités (40 registres + Mode Texte)                   ║
╚══════════════════════════════════════════════════════════════╝
    """)

    logging.info(f"📁 Config: {CONFIG_FILE}")
    logging.info(f"🔌 Broker: {MQTT_BROKER}:{MQTT_PORT}")
    logging.info(f"📡 Port série: {SERIAL_PORT or 'NON DÉTECTÉ'} @ {SERIAL_BAUDRATE} bauds")
    logging.info(f"🏠 Zones: {', '.join(ZONES.values())}")

    if not SERIAL_PORT:
        logging.error("❌ Aucun port série détecté. Vérifiez la connexion USB à la PAC.")
        return

    # Connexion MQTT
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_start()
    except Exception as e:
        logging.error(f"❌ Impossible de se connecter à MQTT: {e}")
        return

    time.sleep(2)
    publish_discovery(mqtt_client)

    # Connexion série
    try:
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=SERIAL_BAUDRATE,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        logging.info(f"✅ Port série ouvert: {SERIAL_PORT}")
    except Exception as e:
        logging.error(f"❌ Erreur port série: {e}")
        return

    # Boucle principale
    logging.info(f"🔄 Lecture toutes les {READ_INTERVAL}s...")
    while True:
        try:
            values = read_all_registers(ser)
            publish_values(mqtt_client, values)
            print_status(values)
        except Exception as e:
            logging.error(f"❌ Erreur: {e}")

        time.sleep(READ_INTERVAL)

if __name__ == "__main__":
    main()
