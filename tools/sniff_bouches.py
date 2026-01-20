#!/usr/bin/env python3
"""
Script de sniff passif bitmap des bouches - Pi 2B via RS485

Ecoute le bus RS485 SANS envoyer de trame.
La telecommande envoie des trames, la PAC repond.
On capture les reponses pour extraire le bitmap des bouches.

AVANTAGE: Telecommande peut rester branchee !

Usage:
    python3 sniff_bouches.py
    python3 sniff_bouches.py --raw     # Affiche trames brutes
    python3 sniff_bouches.py --all     # Affiche toutes les trames (pas juste 80 0b)
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


def parse_bitmap(byte33):
    """Parse le bitmap des bouches"""
    actives = []
    for mask, name in BOUCHES.items():
        if byte33 & mask:
            actives.append(name)
    return actives


def parse_response_80_0b(data, show_raw=False):
    """Parse la reponse 80 0b"""
    if len(data) < 133:
        return None

    if show_raw:
        print(f"[80 0b] Raw ({len(data)} bytes): {data[:50].hex()}...")

    result = {}

    # Mode PAC (byte 20)
    mode = data[20]
    result['mode'] = mode
    result['mode_str'] = MODES.get(mode, f'?({mode})')

    # Bitmap bouches (byte 33)
    bitmap = data[33]
    result['bitmap'] = bitmap
    result['bouches'] = parse_bitmap(bitmap)

    # Consignes zones (offsets 42-53)
    consignes = []
    for i in range(6):
        val = struct.unpack(">H", data[42+i*2:44+i*2])[0]
        consignes.append(val / 100.0)
    result['consignes'] = consignes

    # Temperatures zones (offsets 74-85)
    temperatures = []
    for i in range(6):
        val = struct.unpack(">h", data[74+i*2:76+i*2])[0]
        temperatures.append(val / 100.0)
    result['temperatures'] = temperatures

    return result


def display_result(result):
    """Affiche les resultats"""
    if not result:
        return

    timestamp = time.strftime("%H:%M:%S")

    # Ligne compacte
    bouches_str = ','.join(result['bouches']) if result['bouches'] else '(aucune)'
    print(f"[{timestamp}] Mode: {result['mode_str']:10} | Bitmap: 0x{result['bitmap']:02X} | Bouches: {bouches_str}")


def display_full(result):
    """Affiche les resultats complets"""
    if not result:
        return

    print("\n" + "="*60)
    print(f"Mode PAC: {result['mode_str']}")
    print(f"Bitmap bouches: 0x{result['bitmap']:02X}")

    if result['bouches']:
        print(f"Bouches ACTIVES: {', '.join(result['bouches'])}")
    else:
        print("Bouches ACTIVES: (aucune)")

    print("\nEtat des bouches:")
    zones = ['K1a', 'K1b', 'K3', 'K4', 'K5', 'K6']
    for i, zone in enumerate(zones):
        active = zone in result['bouches']
        consigne = result['consignes'][i]
        temp = result['temperatures'][i]
        status = "OUVERTE" if active else "fermee"
        print(f"  {zone}: {status:8} | Consigne: {consigne:5.1f}C | Temp: {temp:5.1f}C")

    print("="*60)


def main():
    parser = argparse.ArgumentParser(description='Sniff passif bitmap bouches via RS485')
    parser.add_argument('--port', default=SERIAL_PORT,
                        help=f'Port serie (defaut: {SERIAL_PORT})')
    parser.add_argument('--raw', action='store_true',
                        help='Afficher trames brutes')
    parser.add_argument('--all', action='store_true',
                        help='Afficher toutes les trames (pas juste 80 0b)')
    parser.add_argument('--full', action='store_true',
                        help='Affichage complet (pas compact)')

    args = parser.parse_args()

    print(f"Sniff passif sur {args.port} (19200 8E1)")
    print("Telecommande peut rester branchee !")
    print("Ctrl+C pour arreter\n")

    try:
        ser = serial.Serial(args.port, BAUDRATE, parity=PARITY, timeout=0.1)
        buffer = bytearray()
        last_bitmap = None

        while True:
            # Lire les donnees disponibles
            chunk = ser.read(256)
            if chunk:
                buffer.extend(chunk)

            # Chercher les patterns de reponse
            while len(buffer) > 4:
                # Chercher header 01 17 80
                try:
                    idx = buffer.index(bytes([0x01, 0x17, 0x80]))
                except ValueError:
                    # Pas trouve, garder les derniers bytes
                    if len(buffer) > 3:
                        buffer = buffer[-3:]
                    break

                # Verifier le sous-type
                if idx + 4 > len(buffer):
                    break

                subtype = buffer[idx + 3]

                # Reponse 80 0b (133 bytes)
                if subtype == 0x0b:
                    if idx + 133 > len(buffer):
                        break  # Attendre plus de donnees

                    frame = bytes(buffer[idx:idx+133])
                    result = parse_response_80_0b(frame, show_raw=args.raw)

                    if result:
                        # Afficher seulement si bitmap change (ou --full)
                        if args.full:
                            display_full(result)
                        elif result['bitmap'] != last_bitmap:
                            display_result(result)
                            last_bitmap = result['bitmap']

                    buffer = buffer[idx+133:]

                # Autres reponses
                elif args.all:
                    print(f"[{time.strftime('%H:%M:%S')}] Trame 80 {subtype:02x}: {buffer[idx:idx+20].hex()}...")
                    buffer = buffer[idx+4:]
                else:
                    buffer = buffer[idx+4:]

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nArret.")
    except serial.SerialException as e:
        print(f"Erreur port serie: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
