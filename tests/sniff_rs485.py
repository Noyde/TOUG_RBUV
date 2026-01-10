#!/usr/bin/env python3
"""
TOUG_RBUV - Capture RS485 télécommande
Sniffe le bus RS485 et affiche les trames en temps réel.

Usage:
    python3 sniff_rs485.py                    # Affichage temps réel
    python3 sniff_rs485.py --output capture.bin  # Sauvegarde fichier
    python3 sniff_rs485.py --filter 0x17      # Filtre fonction 0x17

Matériel: Pi 2B + convertisseur USB-RS485 Waveshare (FT232RL)
Connexion: En parallèle sur le bus télécommande via Wago

Licence: MIT
"""

import argparse
import sys
import time
import serial
from datetime import datetime

# Configuration RS485 télécommande
SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 19200


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


def verify_crc(data):
    """Vérifier le CRC d'une trame"""
    if len(data) < 4:
        return False
    crc_received = data[-2] | (data[-1] << 8)
    crc_calculated = calculate_crc(data[:-2])
    return crc_received == crc_calculated


def analyze_frame(data):
    """Analyser une trame capturée"""
    if len(data) < 4:
        return "Trame trop courte"

    addr = data[0]
    func = data[1]

    if func == 0x17:
        if len(data) >= 74:
            # Trame 0x17 complète
            niveau = int.from_bytes(data[18:20], 'big')
            onoff = int.from_bytes(data[34:36], 'big')
            type_mode = int.from_bytes(data[36:38], 'big')

            niveaux = {0x0000: "Confort", 0x00C8: "Eco", 0x5678: "Boost"}
            modes = {0x000A: "Clim", 0x000C: "Chauffage"}

            if onoff == 0x0002:
                return "→ OFF"
            else:
                return f"→ {modes.get(type_mode, '?')} {niveaux.get(niveau, '?')}"
        else:
            return f"0x17 partiel ({len(data)} bytes)"

    elif func == 0x03:
        return "Read Holding Registers"
    elif func == 0x06:
        return "Write Single Register"
    elif func == 0x10:
        return "Write Multiple Registers"
    elif func & 0x80:
        error = data[2] if len(data) > 2 else 0
        errors = {1: "illegal function", 2: "illegal data address"}
        return f"Exception: {errors.get(error, f'0x{error:02X}')}"

    return f"Fonction 0x{func:02X}"


def main():
    parser = argparse.ArgumentParser(description="Capture RS485 télécommande")
    parser.add_argument("--port", default=SERIAL_PORT, help=f"Port série (défaut: {SERIAL_PORT})")
    parser.add_argument("--output", "-o", help="Fichier de sortie binaire")
    parser.add_argument("--filter", type=lambda x: int(x, 0), help="Filtrer par fonction (ex: 0x17)")
    parser.add_argument("--duration", "-d", type=int, default=0, help="Durée capture en secondes (0=infini)")
    parser.add_argument("--raw", action="store_true", help="Affichage brut sans analyse")
    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════════╗
║     TOUG_RBUV - Sniff RS485 Télécommande                     ║
║     Ctrl+C pour arrêter                                       ║
╚══════════════════════════════════════════════════════════════╝
    """)

    try:
        ser = serial.Serial(
            port=args.port,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1
        )
        print(f"✅ Port série: {args.port} @ {BAUDRATE} bauds")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

    output_file = None
    if args.output:
        output_file = open(args.output, 'wb')
        print(f"📝 Sauvegarde dans: {args.output}")

    if args.filter:
        print(f"🔍 Filtre actif: fonction 0x{args.filter:02X}")

    print(f"\n{'='*70}")
    print(f"  Capture en cours...")
    print(f"{'='*70}\n")

    start_time = time.time()
    frame_count = 0
    buffer = b""

    try:
        while True:
            if args.duration > 0 and (time.time() - start_time) > args.duration:
                print(f"\n⏱️ Durée atteinte ({args.duration}s)")
                break

            # Lire les données disponibles
            chunk = ser.read(256)
            if not chunk:
                continue

            buffer += chunk

            # Chercher des trames complètes (74 bytes pour 0x17)
            while len(buffer) >= 74:
                # Chercher le début d'une trame (adresse 0x01)
                try:
                    start = buffer.index(0x01)
                    if start > 0:
                        buffer = buffer[start:]
                except ValueError:
                    buffer = b""
                    break

                if len(buffer) < 74:
                    break

                # Extraire la trame potentielle
                frame = buffer[:74]

                # Vérifier si c'est une trame 0x17
                if frame[1] == 0x17:
                    crc_ok = verify_crc(frame)

                    # Filtrer si demandé
                    if args.filter and frame[1] != args.filter:
                        buffer = buffer[74:]
                        continue

                    frame_count += 1
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

                    if args.raw:
                        print(f"[{timestamp}] {frame.hex()}")
                    else:
                        analysis = analyze_frame(frame)
                        crc_str = "✅" if crc_ok else "❌CRC"
                        print(f"[{timestamp}] #{frame_count:3d} | 0x17 | {len(frame)} bytes | {crc_str} | {analysis}")

                    if output_file:
                        output_file.write(frame)

                    buffer = buffer[74:]
                else:
                    # Pas une trame 0x17, avancer d'un byte
                    buffer = buffer[1:]

    except KeyboardInterrupt:
        print(f"\n\n⏹️ Capture arrêtée")
    finally:
        ser.close()
        if output_file:
            output_file.close()

        duration = time.time() - start_time
        print(f"\n{'='*70}")
        print(f"  Résumé: {frame_count} trames capturées en {duration:.1f}s")
        print(f"{'='*70}")


if __name__ == "__main__":
    main()
