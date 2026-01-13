#!/usr/bin/env python3
"""
Script de test envoi trame 0x17 - Pi 2B via RS485

Envoie une trame 0x17 complète (74 bytes) sur le bus télécommande.
Vérifier R9 sur Pi Zero après chaque envoi.

Usage:
    python3 test_send_0x17.py --mode off
    python3 test_send_0x17.py --mode chauffage_confort
    python3 test_send_0x17.py --mode chauffage_eco
    python3 test_send_0x17.py --mode clim_confort
    python3 test_send_0x17.py --mode clim_boost
    python3 test_send_0x17.py --mode vacances_on
    python3 test_send_0x17.py --mode vacances_off
    python3 test_send_0x17.py --read-r9
"""

import serial
import struct
import argparse
import time

# Configuration port série
SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 19200
PARITY = 'E'
TIMEOUT = 2

# Valeurs protocole 0x17
NIVEAU_CONFORT = 0x0000
NIVEAU_ECO = 0x00C8
BOOST_OFF = 0x0000
BOOST_ON = 0x5678
VACANCES_OFF = 0x0000
VACANCES_ON = 0x1234
ONOFF_OFF = 0x0002
ONOFF_ON = 0x0003
TYPE_CLIM = 0x000A
TYPE_CHAUFFAGE = 0x000C

# Compteur global pour les trames
frame_counter = 1


def crc16_modbus(data):
    """Calcul CRC16 Modbus"""
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def build_frame(niveau, boost, vacances, onoff, type_mode):
    """Construit une trame 0x17 de 74 bytes"""
    global frame_counter

    frame = bytearray(74)

    # En-tête fixe
    frame[0] = 0x01  # Adresse esclave
    frame[1] = 0x17  # Fonction Read/Write Multiple
    struct.pack_into(">H", frame, 2, 0x0001)   # Sous-code séquence
    struct.pack_into(">H", frame, 4, 0x0040)   # Longueur lecture (64)
    struct.pack_into(">H", frame, 6, 0x0057)   # Adresse écriture (87)
    struct.pack_into(">H", frame, 8, 0x001F)   # Longueur écriture (31)
    struct.pack_into(">H", frame, 10, 0x7370)  # Signature "sp"
    struct.pack_into(">H", frame, 12, 0x1804)  # Version protocole
    struct.pack_into(">H", frame, 14, frame_counter)  # Compteur
    struct.pack_into(">H", frame, 16, 0xF67A)  # Réservé

    # Champs de contrôle (offsets validés 2025-01-13)
    struct.pack_into(">H", frame, 18, niveau)      # Offset 18-19 : Niveau
    struct.pack_into(">H", frame, 20, boost)       # Offset 20-21 : Boost
    struct.pack_into(">H", frame, 22, 0x0000)      # Offset 22-23 : Padding
    struct.pack_into(">H", frame, 24, 0x0000)      # Offset 24-25 : Flag service
    struct.pack_into(">H", frame, 26, 0x0384)      # Offset 26-27 : Débit nominal (900)
    struct.pack_into(">H", frame, 28, 0x0017)      # Offset 28-29 : PSE nominal (23)
    struct.pack_into(">H", frame, 30, 0x00F0)      # Offset 30-31 : Débit 1 bouche (240)
    struct.pack_into(">H", frame, 32, 0x000C)      # Offset 32-33 : PSE mini (12)
    struct.pack_into(">H", frame, 34, vacances)    # Offset 34-35 : Vacances
    struct.pack_into(">H", frame, 36, onoff)       # Offset 36-37 : On/Off
    struct.pack_into(">H", frame, 38, type_mode)   # Offset 38-39 : Type mode

    # Consignes zones (0x7FFE = pas de changement)
    for i in range(40, 70, 2):
        struct.pack_into(">H", frame, i, 0x7FFE)

    # Padding final
    struct.pack_into(">H", frame, 70, 0x0000)

    # CRC16 Modbus (little-endian)
    crc = crc16_modbus(frame[:72])
    struct.pack_into("<H", frame, 72, crc)

    frame_counter += 1
    return frame


def send_frame(frame, verbose=True):
    """Envoie une trame et lit la réponse"""
    if verbose:
        print(f"Envoi ({len(frame)} bytes):")
        print(" ".join(f"{b:02x}" for b in frame))

    ser = serial.Serial(SERIAL_PORT, BAUDRATE, parity=PARITY, timeout=TIMEOUT)
    ser.reset_input_buffer()
    ser.write(frame)
    ser.flush()
    time.sleep(0.2)
    response = ser.read(256)
    ser.close()

    if verbose:
        print(f"\nRéponse ({len(response)} bytes):")
        if response:
            print(" ".join(f"{b:02x}" for b in response))
        else:
            print("(aucune réponse)")

    return response


def read_r9():
    """Lit le registre R9 (mode PAC)"""
    try:
        import minimalmodbus
    except ImportError:
        print("Erreur: minimalmodbus non installé (pip install minimalmodbus)")
        return None

    i = minimalmodbus.Instrument(SERIAL_PORT, 1)
    i.serial.baudrate = BAUDRATE
    i.serial.parity = PARITY
    i.serial.timeout = 1
    i.serial.reset_input_buffer()
    time.sleep(0.1)
    i.serial.reset_input_buffer()

    r9 = i.read_register(9)
    modes = {2: "Clim", 4: "Chauffage", 5: "Off"}
    mode_str = modes.get(r9, "Inconnu")
    print(f"R9 = {r9} ({mode_str})")
    return r9


# Définition des modes
MODES = {
    'off': {
        'niveau': NIVEAU_CONFORT,
        'boost': BOOST_OFF,
        'vacances': VACANCES_OFF,
        'onoff': ONOFF_OFF,
        'type': TYPE_CHAUFFAGE,
        'description': 'Off'
    },
    'chauffage_confort': {
        'niveau': NIVEAU_CONFORT,
        'boost': BOOST_OFF,
        'vacances': VACANCES_OFF,
        'onoff': ONOFF_ON,
        'type': TYPE_CHAUFFAGE,
        'description': 'Chauffage Confort'
    },
    'chauffage_eco': {
        'niveau': NIVEAU_ECO,
        'boost': BOOST_OFF,
        'vacances': VACANCES_OFF,
        'onoff': ONOFF_ON,
        'type': TYPE_CHAUFFAGE,
        'description': 'Chauffage Eco'
    },
    'clim_confort': {
        'niveau': NIVEAU_CONFORT,
        'boost': BOOST_OFF,
        'vacances': VACANCES_OFF,
        'onoff': ONOFF_ON,
        'type': TYPE_CLIM,
        'description': 'Clim Confort'
    },
    'clim_boost': {
        'niveau': NIVEAU_CONFORT,
        'boost': BOOST_ON,
        'vacances': VACANCES_OFF,
        'onoff': ONOFF_ON,
        'type': TYPE_CLIM,
        'description': 'Clim Boost'
    },
    'vacances_on': {
        'niveau': NIVEAU_CONFORT,
        'boost': BOOST_OFF,
        'vacances': VACANCES_ON,
        'onoff': ONOFF_ON,
        'type': TYPE_CHAUFFAGE,
        'description': 'Vacances On'
    },
    'vacances_off': {
        'niveau': NIVEAU_CONFORT,
        'boost': BOOST_OFF,
        'vacances': VACANCES_OFF,
        'onoff': ONOFF_ON,
        'type': TYPE_CHAUFFAGE,
        'description': 'Vacances Off (Chauffage Confort)'
    },
}


def main():
    parser = argparse.ArgumentParser(description='Test envoi trame 0x17')
    parser.add_argument('--mode', choices=list(MODES.keys()),
                        help='Mode à envoyer')
    parser.add_argument('--read-r9', action='store_true',
                        help='Lire le registre R9')
    parser.add_argument('--port', default=SERIAL_PORT,
                        help=f'Port série (défaut: {SERIAL_PORT})')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Mode silencieux')

    args = parser.parse_args()

    global SERIAL_PORT
    SERIAL_PORT = args.port

    if args.read_r9:
        read_r9()
        return

    if not args.mode:
        parser.print_help()
        print("\nModes disponibles:")
        for name, config in MODES.items():
            print(f"  {name}: {config['description']}")
        return

    config = MODES[args.mode]
    print(f"=== Envoi: {config['description']} ===\n")

    frame = build_frame(
        niveau=config['niveau'],
        boost=config['boost'],
        vacances=config['vacances'],
        onoff=config['onoff'],
        type_mode=config['type']
    )

    send_frame(frame, verbose=not args.quiet)

    print("\n=== Vérification R9 ===")
    time.sleep(0.3)
    read_r9()


if __name__ == '__main__':
    main()
