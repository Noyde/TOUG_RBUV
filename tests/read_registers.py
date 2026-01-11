#!/usr/bin/env python3
"""
TOUG_RBUV - Script de test lecture registres Modbus
Pour Raspberry Pi Zero W connecté via USB

Usage:
    python3 read_registers.py                    # Tous les registres connus
    python3 read_registers.py --group system     # Groupe spécifique
    python3 read_registers.py --register 9       # Registre spécifique
    python3 read_registers.py --toug             # Registres TOUG étendus
    python3 read_registers.py --all --output rapport.md  # Export markdown

Groupes disponibles: system, consignes, temperatures, ventilation,
                     compresseur, pac, eev, debits

Licence: MIT
"""

import argparse
import sys
import time
import serial
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

SERIAL_PORT = "/dev/ttyACM1"
BAUDRATE = 1200
MODBUS_ADDRESS = 0x01
TIMEOUT = 1

# =============================================================================
# REGISTRES PAR GROUPE
# =============================================================================

REGISTERS = {
    # Système
    "system": {
        1: {"name": "Version Firmware", "unit": "", "divisor": 1, "signed": False},
        3: {"name": "Durée ON", "unit": "min", "divisor": 1, "signed": False},
        9: {"name": "Mode PAC", "unit": "", "divisor": 1, "signed": False},
    },

    # Consignes thermostats (lecture seule - radio 868MHz)
    "consignes": {
        20: {"name": "Consigne Zone 1", "unit": "°C", "divisor": 100, "signed": False},
        21: {"name": "Consigne Zone 1 bis", "unit": "°C", "divisor": 100, "signed": False},
        22: {"name": "Consigne Zone 2", "unit": "°C", "divisor": 100, "signed": False},
        23: {"name": "Consigne Zone 3", "unit": "°C", "divisor": 100, "signed": False},
        24: {"name": "Consigne Zone 4", "unit": "°C", "divisor": 100, "signed": False},
        25: {"name": "Consigne Zone 5", "unit": "°C", "divisor": 100, "signed": False},
    },

    # Températures zones (mapping RBUV : R36/R37 = même thermostat Zone 1)
    "temperatures": {
        36: {"name": "Température Zone 1", "unit": "°C", "divisor": 100, "signed": True},
        37: {"name": "Température Zone 1 bis", "unit": "°C", "divisor": 100, "signed": True},
        38: {"name": "Température Zone 2", "unit": "°C", "divisor": 100, "signed": True},
        39: {"name": "Température Zone 3", "unit": "°C", "divisor": 100, "signed": True},
        40: {"name": "Température Zone 4", "unit": "°C", "divisor": 100, "signed": True},
        41: {"name": "Température Zone 5", "unit": "°C", "divisor": 100, "signed": True},
    },

    # Ventilation
    "ventilation": {
        60: {"name": "Consigne Ventilateur", "unit": "rpm", "divisor": 1, "signed": False},
        61: {"name": "Vitesse Ventilateur", "unit": "rpm", "divisor": 1, "signed": False},
        106: {"name": "Niveau Ventilation UE", "unit": "", "divisor": 1, "signed": False},
        125: {"name": "Heures Ventilateur", "unit": "h", "divisor": 1, "signed": False},
    },

    # Compresseur
    "compresseur": {
        65: {"name": "Consigne Fréquence", "unit": "Hz", "divisor": 10, "signed": False},
        66: {"name": "Fréquence Compresseur", "unit": "Hz", "divisor": 10, "signed": False},
        127: {"name": "Heures Compresseur", "unit": "h", "divisor": 1, "signed": False},
    },

    # Températures PAC internes
    "pac": {
        111: {"name": "T° Air Repris UI", "unit": "°C", "divisor": 100, "signed": True},
        112: {"name": "T° Extérieure", "unit": "°C", "divisor": 100, "signed": True},
        114: {"name": "T° Échangeur UI", "unit": "°C", "divisor": 100, "signed": True},
        115: {"name": "T° Échangeur UE", "unit": "°C", "divisor": 100, "signed": True},
        117: {"name": "T° Sortie Compresseur", "unit": "°C", "divisor": 100, "signed": False},
    },

    # Vannes EEV
    "eev": {
        104: {"name": "EEV1", "unit": "Pls", "divisor": 1, "signed": False},
        105: {"name": "EEV2", "unit": "Pls", "divisor": 1, "signed": False},
    },

    # Débits / Pressions
    "debits": {
        247: {"name": "PSE Débit Nominal", "unit": "Pa", "divisor": 1, "signed": False},
        248: {"name": "PSE Débit Mini", "unit": "Pa", "divisor": 1, "signed": False},
        249: {"name": "Débit 1 Bouche", "unit": "m³/h", "divisor": 1, "signed": False},
        250: {"name": "Débit Nominal", "unit": "m³/h", "divisor": 1, "signed": False},
        251: {"name": "Pression Statique Ext", "unit": "Pa", "divisor": 1, "signed": False},
    },
}

# Registres TOUG étendus (à tester sur RBUV)
TOUG_EXTENDED = {
    "toug_system": {
        14: {"name": "Panel ID (LSB)", "unit": "", "divisor": 1, "signed": False},
        15: {"name": "Panel ID (MSB)", "unit": "", "divisor": 1, "signed": False},
        # NOTE: R16/R17 non fonctionnels sur RBUV via USB (valeurs incohérentes)
        # 16: {"name": "Date encodée", "unit": "", "divisor": 1, "signed": False},
        # 17: {"name": "Heure encodée", "unit": "", "divisor": 1, "signed": False},
        51: {"name": "Protection Compresseur", "unit": "", "divisor": 1, "signed": False},
        90: {"name": "Code Défaut UE", "unit": "", "divisor": 1, "signed": False},
        131: {"name": "État Dégivrage", "unit": "", "divisor": 1, "signed": False},
    },

    "toug_temperatures": {
        42: {"name": "T° Échangeur Ext (ThoR1)", "unit": "°C", "divisor": 100, "signed": True},
        44: {"name": "T° Sortie Compresseur TOUG", "unit": "°C", "divisor": 100, "signed": False},
        49: {"name": "Courant Compresseur", "unit": "A", "divisor": 100, "signed": False},
    },

    "toug_ventilation": {
        72: {"name": "Temps ON Compresseur (LSB)", "unit": "s", "divisor": 1, "signed": False},
        73: {"name": "Temps ON Compresseur (MSB)", "unit": "", "divisor": 1, "signed": False},
        91: {"name": "Position EEV1", "unit": "Pls", "divisor": 1, "signed": False},
        93: {"name": "Vitesse Ventilateur UE", "unit": "", "divisor": 1, "signed": False},
    },

    "toug_extended": {
        5029: {"name": "Canaux Actifs", "unit": "", "divisor": 1, "signed": False},
        6021: {"name": "État Circuit Frigo", "unit": "", "divisor": 1, "signed": False},
        20063: {"name": "État Filtres", "unit": "", "divisor": 1, "signed": False},
        30026: {"name": "Nb Zones Configurées", "unit": "", "divisor": 1, "signed": False},
    },

    # Ces registres ne fonctionnent sur AUCUN modèle (confirmé par @djtef)
    "toug_consignes_ko": {
        31100: {"name": "Consigne Zone K1a (KO)", "unit": "°C", "divisor": 100, "signed": False},
        31101: {"name": "Consigne Zone K1b (KO)", "unit": "°C", "divisor": 100, "signed": False},
        31102: {"name": "Consigne Zone K2 (KO)", "unit": "°C", "divisor": 100, "signed": False},
        31103: {"name": "Consigne Zone K3 (KO)", "unit": "°C", "divisor": 100, "signed": False},
        31104: {"name": "Consigne Zone K4 (KO)", "unit": "°C", "divisor": 100, "signed": False},
    },
}

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
    """Calcul CRC16 Modbus (polynôme 0xA001)"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def read_register(ser, address, register):
    """
    Lire un registre Modbus (FC 0x03)
    Retourne (valeur_brute, erreur) - erreur est None si OK
    """
    request = bytes([
        address,
        0x03,
        (register >> 8) & 0xFF,
        register & 0xFF,
        0x00,
        0x01
    ])
    crc = calculate_crc(request)
    request += bytes([crc & 0xFF, (crc >> 8) & 0xFF])

    ser.reset_input_buffer()
    ser.write(request)
    time.sleep(0.15)

    response = ser.read(7)

    if len(response) < 5:
        return None, "timeout"

    # Vérifier si c'est une erreur Modbus
    if response[1] & 0x80:
        error_code = response[2]
        error_names = {
            1: "illegal function",
            2: "illegal data address",
            3: "illegal data value",
            4: "slave device failure"
        }
        return None, error_names.get(error_code, f"error 0x{error_code:02X}")

    if len(response) == 7 and response[1] == 0x03:
        value = (response[3] << 8) | response[4]
        return value, None

    return None, "invalid response"


def format_value(raw, reg_info):
    """Formater une valeur brute avec diviseur et signe"""
    if raw is None:
        return None

    # Gestion des valeurs signées
    if reg_info.get("signed", False) and raw > 32767:
        raw = raw - 65536

    value = raw / reg_info["divisor"]
    return value


# =============================================================================
# FONCTIONS DE TEST
# =============================================================================

def test_registers(ser, registers_dict, group_name=""):
    """Tester un groupe de registres"""
    results = []

    for addr, info in registers_dict.items():
        raw, error = read_register(ser, MODBUS_ADDRESS, addr)

        if error:
            status = f"❌ {error}"
            value_str = "-"
        else:
            value = format_value(raw, info)
            status = "✅"

            # Formatage selon l'unité
            if info["unit"] == "°C":
                value_str = f"{value:.2f} °C"
            elif info["unit"] == "Hz":
                value_str = f"{value:.1f} Hz"
            elif info["unit"]:
                value_str = f"{value:.0f} {info['unit']}"
            else:
                # Cas spécial pour le mode PAC
                if addr == 9 and value is not None:
                    mode_name = MODE_PAC.get(int(value), f"Inconnu")
                    value_str = f"{int(value)} ({mode_name})"
                else:
                    value_str = f"{value:.0f}"

        results.append({
            "address": addr,
            "name": info["name"],
            "raw": raw,
            "value": value_str,
            "status": status,
            "error": error
        })

        print(f"  R{addr:5d} | {info['name']:30s} | {value_str:20s} | {status}")
        time.sleep(0.2)  # 200ms minimum pour 1200 bauds

    return results


def test_group(ser, group_name):
    """Tester un groupe spécifique"""
    if group_name in REGISTERS:
        print(f"\n{'='*70}")
        print(f"  Groupe: {group_name.upper()}")
        print(f"{'='*70}")
        return test_registers(ser, REGISTERS[group_name], group_name)
    elif group_name in TOUG_EXTENDED:
        print(f"\n{'='*70}")
        print(f"  Groupe TOUG: {group_name.upper()}")
        print(f"{'='*70}")
        return test_registers(ser, TOUG_EXTENDED[group_name], group_name)
    else:
        print(f"❌ Groupe inconnu: {group_name}")
        print(f"   Groupes disponibles: {', '.join(list(REGISTERS.keys()) + list(TOUG_EXTENDED.keys()))}")
        return []


def test_all(ser, include_toug=False):
    """Tester tous les registres"""
    all_results = {}

    for group_name, registers in REGISTERS.items():
        all_results[group_name] = test_group(ser, group_name)

    if include_toug:
        print(f"\n{'#'*70}")
        print(f"  REGISTRES TOUG ÉTENDUS (à valider sur RBUV)")
        print(f"{'#'*70}")
        for group_name, registers in TOUG_EXTENDED.items():
            all_results[group_name] = test_group(ser, group_name)

    return all_results


def test_single_register(ser, address):
    """Tester un registre spécifique"""
    # Chercher le registre dans tous les groupes
    reg_info = None
    for group in list(REGISTERS.values()) + list(TOUG_EXTENDED.values()):
        if address in group:
            reg_info = group[address]
            break

    if reg_info is None:
        reg_info = {"name": f"Registre {address}", "unit": "", "divisor": 1, "signed": False}

    print(f"\n{'='*70}")
    print(f"  Test registre {address}")
    print(f"{'='*70}")

    raw, error = read_register(ser, MODBUS_ADDRESS, address)

    if error:
        print(f"  R{address} | {reg_info['name']} | ❌ {error}")
    else:
        value = format_value(raw, reg_info)
        print(f"  R{address} | {reg_info['name']} | Brut: {raw} | Valeur: {value} {reg_info['unit']} | ✅")

    return {"address": address, "raw": raw, "error": error}


# =============================================================================
# EXPORT MARKDOWN
# =============================================================================

def export_markdown(results, filename):
    """Exporter les résultats en markdown"""
    with open(filename, 'w') as f:
        f.write(f"# Rapport de test TOUG_RBUV\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Port**: {SERIAL_PORT}\n")
        f.write(f"**Baudrate**: {BAUDRATE}\n\n")

        for group_name, group_results in results.items():
            f.write(f"## {group_name.replace('_', ' ').title()}\n\n")
            f.write("| Registre | Description | Valeur | Statut |\n")
            f.write("|----------|-------------|--------|--------|\n")

            for r in group_results:
                f.write(f"| R{r['address']} | {r['name']} | {r['value']} | {r['status']} |\n")

            f.write("\n")

        # Résumé
        total = sum(len(g) for g in results.values())
        ok = sum(1 for g in results.values() for r in g if r['error'] is None)
        f.write(f"---\n\n")
        f.write(f"**Résumé**: {ok}/{total} registres OK\n")

    print(f"\n📄 Rapport exporté: {filename}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Test lecture registres Modbus PAC Aldes T.One RBUV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python3 read_registers.py                    # Tous les registres RBUV
  python3 read_registers.py --group system     # Groupe système uniquement
  python3 read_registers.py --register 9       # Registre mode PAC
  python3 read_registers.py --toug             # Inclure registres TOUG étendus
  python3 read_registers.py --all --output rapport.md  # Export markdown

Groupes: system, consignes, temperatures, ventilation, compresseur, pac, eev, debits
        """
    )

    parser.add_argument("--port", default=SERIAL_PORT,
                        help=f"Port série (défaut: {SERIAL_PORT})")
    parser.add_argument("--group", "-g",
                        help="Groupe de registres à tester")
    parser.add_argument("--register", "-r", type=int,
                        help="Registre spécifique à tester")
    parser.add_argument("--toug", action="store_true",
                        help="Inclure les registres TOUG étendus")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Tester tous les registres")
    parser.add_argument("--output", "-o",
                        help="Fichier de sortie markdown")

    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════════╗
║     TOUG_RBUV - Test Lecture Registres Modbus                ║
║     https://github.com/Noyde/TOUG_RBUV                       ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Connexion série
    try:
        ser = serial.Serial(
            port=args.port,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=TIMEOUT
        )
        print(f"✅ Port série ouvert: {args.port} @ {BAUDRATE} bauds")
        time.sleep(1)  # Stabilisation connexion USB
        ser.reset_input_buffer()
    except Exception as e:
        print(f"❌ Erreur ouverture port série: {e}")
        sys.exit(1)

    try:
        if args.register is not None:
            # Test registre unique
            test_single_register(ser, args.register)
        elif args.group:
            # Test groupe
            results = {args.group: test_group(ser, args.group)}
            if args.output:
                export_markdown(results, args.output)
        else:
            # Test tous les registres
            results = test_all(ser, include_toug=args.toug)
            if args.output:
                export_markdown(results, args.output)

        # Résumé
        print(f"\n{'='*70}")
        print("  Test terminé")
        print(f"{'='*70}")

    except KeyboardInterrupt:
        print("\n⏹️  Test interrompu")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
