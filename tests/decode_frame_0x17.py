#!/usr/bin/env python3
"""
TOUG_RBUV - Décodeur de trames 0x17
Analyse une trame 74 bytes capturée depuis la télécommande.

Usage:
    python3 decode_frame_0x17.py capture.bin
    python3 decode_frame_0x17.py --hex "0117004100..."
    echo "0117..." | python3 decode_frame_0x17.py --stdin

Licence: MIT
"""

import argparse
import sys

# Structure de la trame 0x17 (74 bytes)
FRAME_STRUCTURE = {
    (0, 1): ("Adresse Modbus", None),
    (1, 1): ("Fonction", None),
    (2, 2): ("Sous-code séquence", "sequence"),
    (4, 2): ("Longueur", None),
    (6, 2): ("Constante 1", None),
    (8, 2): ("Constante 2", None),
    (10, 2): ("Signature", "signature"),
    (12, 2): ("Version", None),
    (14, 4): ("Réservé", None),
    (18, 2): ("Niveau (Eco/Confort/Boost)", "niveau"),
    (20, 8): ("Padding 1", None),
    (28, 2): ("Débit nominal", "debit_nominal"),
    (30, 2): ("PSE débit nominal", "pse_nominal"),
    (32, 2): ("Débit mini / Vacances", "vacances"),
    (34, 2): ("PSE mini / On-Off", "onoff"),
    (36, 2): ("Type mode", "type_mode"),
    (38, 2): ("Padding 2", None),
    (40, 30): ("Consignes (non modifiables)", None),
    (70, 2): ("Padding 3", None),
    (72, 2): ("CRC16 Modbus", "crc"),
}

# Valeurs connues
NIVEAUX = {
    0x0000: "Confort",
    0x00C8: "Eco",
    0x5678: "Boost",
}

ONOFF = {
    0x0002: "Off",
    0x0003: "On",
}

TYPE_MODE = {
    0x000A: "Climatisation",
    0x000C: "Chauffage",
}

VACANCES = {
    0x0000: "Vacances Off",
    0x1234: "Vacances On",
}

SEQUENCE = {
    0x0001: "Séquence 1/4",
    0x0041: "Séquence 2/4",
    0x0081: "Séquence 3/4",
    0x00C1: "Séquence 4/4",
}


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


def decode_frame(data):
    """Décoder une trame 0x17"""
    if len(data) < 74:
        print(f"⚠️ Trame trop courte: {len(data)} bytes (attendu: 74)")
        return

    print(f"\n{'='*70}")
    print(f"  Décodage trame 0x17 ({len(data)} bytes)")
    print(f"{'='*70}\n")

    # Afficher la trame brute
    print(f"Trame hex: {data[:74].hex()}\n")

    # Décoder chaque champ
    for (offset, size), (name, field_type) in FRAME_STRUCTURE.items():
        raw = data[offset:offset+size]

        if size == 1:
            value = raw[0]
            hex_str = f"0x{value:02X}"
        else:
            value = int.from_bytes(raw, 'big')
            hex_str = f"0x{value:04X}"

        # Interpréter les champs connus
        interpretation = ""
        if field_type == "niveau":
            interpretation = f" → {NIVEAUX.get(value, 'Inconnu')}"
        elif field_type == "onoff":
            interpretation = f" → {ONOFF.get(value, 'Inconnu')}"
        elif field_type == "type_mode":
            interpretation = f" → {TYPE_MODE.get(value, 'Inconnu')}"
        elif field_type == "vacances":
            if value in VACANCES:
                interpretation = f" → {VACANCES[value]}"
            else:
                interpretation = f" → Débit mini: {value} m³/h"
        elif field_type == "sequence":
            interpretation = f" → {SEQUENCE.get(value, 'Inconnu')}"
        elif field_type == "signature":
            try:
                interpretation = f' → "{raw.decode("ascii")}"'
            except:
                pass
        elif field_type == "crc":
            # Vérifier le CRC
            calculated = calculate_crc(data[:72])
            crc_bytes = calculated.to_bytes(2, 'little')
            if raw == crc_bytes:
                interpretation = " → ✅ CRC valide"
            else:
                interpretation = f" → ❌ CRC invalide (attendu: 0x{calculated:04X})"

        print(f"  [{offset:2d}-{offset+size-1:2d}] {name:35s} = {hex_str}{interpretation}")

    # Résumé du mode
    print(f"\n{'='*70}")
    print(f"  Résumé")
    print(f"{'='*70}")

    niveau = int.from_bytes(data[18:20], 'big')
    vacances = int.from_bytes(data[32:34], 'big')
    onoff = int.from_bytes(data[34:36], 'big')
    type_mode = int.from_bytes(data[36:38], 'big')

    mode_str = ""
    if onoff == 0x0002:
        mode_str = "Off"
    elif vacances == 0x1234:
        mode_str = "Vacances"
    else:
        type_str = TYPE_MODE.get(type_mode, "?")
        niveau_str = NIVEAUX.get(niveau, "?")
        mode_str = f"{type_str} {niveau_str}"

    print(f"  Mode détecté: {mode_str}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Décodeur de trames 0x17")
    parser.add_argument("file", nargs="?", help="Fichier binaire à analyser")
    parser.add_argument("--hex", help="Trame en hexadécimal")
    parser.add_argument("--stdin", action="store_true", help="Lire depuis stdin")
    parser.add_argument("--offset", type=int, default=0, help="Offset dans le fichier")
    args = parser.parse_args()

    if args.hex:
        # Depuis une chaîne hex
        try:
            data = bytes.fromhex(args.hex.replace(" ", ""))
        except ValueError as e:
            print(f"❌ Erreur hex: {e}")
            sys.exit(1)
    elif args.stdin:
        # Depuis stdin
        hex_input = sys.stdin.read().strip().replace(" ", "").replace("\n", "")
        data = bytes.fromhex(hex_input)
    elif args.file:
        # Depuis un fichier
        with open(args.file, 'rb') as f:
            f.seek(args.offset)
            data = f.read(74)
    else:
        parser.print_help()
        sys.exit(1)

    decode_frame(data)


if __name__ == "__main__":
    main()
