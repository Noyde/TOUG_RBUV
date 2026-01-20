#!/usr/bin/env python3
"""
Script de lecture bitmap des bouches - Pi 2B via RS485

Envoie une trame 0x17 et parse la reponse pour extraire:
- Byte 33: Bitmap des bouches actives
- Mode PAC (byte 20)
- Consignes zones (offsets 42-53)
- Temperatures zones (offsets 74-85)

Usage:
    python3 read_bouches.py
    python3 read_bouches.py --loop       # Mode continu (5s)
    python3 read_bouches.py --loop 2     # Mode continu (2s)
    python3 read_bouches.py --raw        # Affiche trame brute
"""

import serial
import struct
import argparse
import time
import sys

# Configuration port serie
SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 19200
PARITY = 'E'
TIMEOUT = 2

# Mapping bouches
BOUCHES = {
    0x01: 'K1a',
    0x02: 'K1b',
    0x04: 'K3',
    0x08: 'K4',
    0x10: 'K5',
    0x20: 'K6',
}

# Mapping modes
MODES = {
    2: 'Clim',
    4: 'Chauffage',
    5: 'Off',
}

# Compteur trame
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


def build_read_frame():
    """Construit une trame 0x17 de lecture (mode chauffage confort)"""
    global frame_counter

    frame = bytearray(74)

    # En-tete fixe
    frame[0] = 0x01  # Adresse esclave
    frame[1] = 0x17  # Fonction Read/Write Multiple
    struct.pack_into(">H", frame, 2, 0x0001)   # Sous-code sequence
    struct.pack_into(">H", frame, 4, 0x0040)   # Longueur lecture (64)
    struct.pack_into(">H", frame, 6, 0x0057)   # Adresse ecriture (87)
    struct.pack_into(">H", frame, 8, 0x001F)   # Longueur ecriture (31)
    struct.pack_into(">H", frame, 10, 0x7370)  # Signature "sp"
    struct.pack_into(">H", frame, 12, 0x1804)  # Version protocole
    struct.pack_into(">H", frame, 14, frame_counter)  # Compteur
    struct.pack_into(">H", frame, 16, 0xF67A)  # Reserve

    # Champs de controle - mode lecture seule (pas de changement)
    struct.pack_into(">H", frame, 18, 0x0000)  # Niveau Confort
    struct.pack_into(">H", frame, 20, 0x0000)  # Boost Off
    struct.pack_into(">H", frame, 22, 0x0000)  # Padding
    struct.pack_into(">H", frame, 24, 0x0000)  # Flag service
    struct.pack_into(">H", frame, 26, 0x0384)  # Debit nominal (900)
    struct.pack_into(">H", frame, 28, 0x0017)  # PSE nominal (23)
    struct.pack_into(">H", frame, 30, 0x00F0)  # Debit 1 bouche (240)
    struct.pack_into(">H", frame, 32, 0x000C)  # PSE mini (12)
    struct.pack_into(">H", frame, 34, 0x0000)  # Vacances Off
    struct.pack_into(">H", frame, 36, 0x0003)  # On
    struct.pack_into(">H", frame, 38, 0x000C)  # Chauffage

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


def parse_bitmap(byte33):
    """Parse le bitmap des bouches"""
    actives = []
    for mask, name in BOUCHES.items():
        if byte33 & mask:
            actives.append(name)
    return actives


def parse_response(response, show_raw=False):
    """Parse la reponse 0x17"""
    if len(response) < 133:
        print(f"Reponse trop courte: {len(response)} bytes (attendu ~133)")
        if show_raw and response:
            print("Raw:", " ".join(f"{b:02x}" for b in response))
        return None

    # Verifier header
    if response[0:4] != bytes([0x01, 0x17, 0x80, 0x0b]):
        print(f"Header inattendu: {response[0:4].hex()}")
        # Chercher le bon header
        idx = response.find(bytes([0x01, 0x17, 0x80, 0x0b]))
        if idx > 0:
            print(f"Header trouve a l'offset {idx}, realignement...")
            response = response[idx:]
        else:
            if show_raw:
                print("Raw:", " ".join(f"{b:02x}" for b in response))
            return None

    if show_raw:
        print("Raw:", " ".join(f"{b:02x}" for b in response[:133]))

    result = {}

    # Mode PAC (byte 20)
    mode = response[20]
    result['mode'] = mode
    result['mode_str'] = MODES.get(mode, f'Inconnu({mode})')

    # Bitmap bouches (byte 33)
    bitmap = response[33]
    result['bitmap'] = bitmap
    result['bouches'] = parse_bitmap(bitmap)

    # Consignes zones (offsets 42-53, 6x2 bytes)
    consignes = []
    for i in range(6):
        val = struct.unpack(">H", response[42+i*2:44+i*2])[0]
        consignes.append(val / 100.0)
    result['consignes'] = consignes

    # Temperatures zones (offsets 74-85, 6x2 bytes)
    temperatures = []
    for i in range(6):
        val = struct.unpack(">h", response[74+i*2:76+i*2])[0]  # signe
        temperatures.append(val / 100.0)
    result['temperatures'] = temperatures

    return result


def display_result(result):
    """Affiche les resultats"""
    if not result:
        return

    print("\n" + "="*50)
    print(f"Mode PAC: {result['mode_str']}")
    print(f"Bitmap bouches: 0x{result['bitmap']:02X}")

    # Afficher bouches actives
    if result['bouches']:
        print(f"Bouches ACTIVES: {', '.join(result['bouches'])}")
    else:
        print("Bouches ACTIVES: (aucune)")

    # Afficher etat de chaque bouche
    print("\nEtat des bouches:")
    zones = ['K1a', 'K1b', 'K3', 'K4', 'K5', 'K6']
    for i, zone in enumerate(zones):
        active = zone in result['bouches']
        consigne = result['consignes'][i]
        temp = result['temperatures'][i]
        status = "OUVERTE" if active else "fermee"
        print(f"  {zone}: {status:8} | Consigne: {consigne:5.1f}C | Temp: {temp:5.1f}C")

    print("="*50)


def main():
    parser = argparse.ArgumentParser(description='Lecture bitmap bouches via 0x17')
    parser.add_argument('--port', default=SERIAL_PORT,
                        help=f'Port serie (defaut: {SERIAL_PORT})')
    parser.add_argument('--loop', nargs='?', const=5, type=float,
                        help='Mode continu avec intervalle en secondes (defaut: 5)')
    parser.add_argument('--raw', action='store_true',
                        help='Afficher trame brute')

    args = parser.parse_args()

    global SERIAL_PORT
    SERIAL_PORT = args.port

    try:
        while True:
            # Construire et envoyer trame
            frame = build_read_frame()

            ser = serial.Serial(SERIAL_PORT, BAUDRATE, parity=PARITY, timeout=TIMEOUT)
            ser.reset_input_buffer()
            ser.write(frame)
            ser.flush()
            time.sleep(0.2)
            response = ser.read(256)
            ser.close()

            # Parser et afficher
            result = parse_response(response, show_raw=args.raw)
            display_result(result)

            if not args.loop:
                break

            time.sleep(args.loop)
            print("\n" + "-"*50)

    except KeyboardInterrupt:
        print("\nArret.")
    except serial.SerialException as e:
        print(f"Erreur port serie: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
