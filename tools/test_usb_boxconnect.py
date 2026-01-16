#!/usr/bin/env python3
"""
Test du protocole USB Box Connect sur RBUV

Basé sur les découvertes de @djtef (forum HACF, janvier 2025)
Protocole propriétaire utilisé par la passerelle Box Connect Aldes

IMPORTANT: Arrêter pac_aldes_mqtt.py avant d'exécuter ce script !
    sudo systemctl stop pac_aldes

Usage:
    python3 test_usb_boxconnect.py [port]

Exemples:
    python3 test_usb_boxconnect.py              # Auto-détection
    python3 test_usb_boxconnect.py /dev/ttyACM1 # Port explicite
"""

import serial
import serial.tools.list_ports
import time
import sys
import struct
from datetime import datetime

# Configuration protocole Box Connect
BAUDRATE = 115200
PARITY = serial.PARITY_NONE
STOPBITS = serial.STOPBITS_ONE
BYTESIZE = serial.EIGHTBITS
TIMEOUT = 2

# Headers protocole
HEADER_PAC_OUT = bytes([0xFA, 0xFD])      # PAC → Passerelle
HEADER_GW_IN = bytes([0xFD, 0xFA])        # Passerelle → PAC
HEADER_PAC_RESP = bytes([0xFF, 0xFD])     # Réponse PAC

# Trames connues
PING = bytes([0xFA, 0xFD, 0x07, 0xFF, 0x4A, 0xFE, 0xBB])
PONG = bytes([0xFD, 0xFA, 0x07, 0xFF, 0x13, 0xFE, 0xF2])
INIT_STANDARD = bytes([0x02, 0x03, 0x04, 0x20, 0x00, 0x01, 0x02, 0x42, 0xA2])

# Requêtes de lecture
REQ_CONFIG = bytes([0xFD, 0xFA, 0x08, 0xFF, 0x41, 0x21, 0xFE, 0xA2])  # Type 0x21
REQ_MODBUS = bytes([0x02, 0x03, 0x04, 0x20, 0x00, 0x01, 0x84, 0xC3])  # Modbus encapsulé
REQ_PROG = bytes([0xFD, 0xFA, 0x08, 0xFF, 0x42, 0x22, 0xFE, 0xA0])    # Type 0x23


def find_port():
    """Auto-détection du port USB PAC"""
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if 'ACM' in port.device or 'USB' in port.device:
            print(f"Port trouvé: {port.device} ({port.description})")
            return port.device
    return None


def hex_dump(data, prefix=""):
    """Affiche les données en hexadécimal formaté"""
    if not data:
        print(f"{prefix}(vide)")
        return

    hex_str = ' '.join(f'{b:02X}' for b in data)
    ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)

    # Affichage par lignes de 16 bytes
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02X}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        print(f"{prefix}{i:04X}: {hex_part:<48} {ascii_part}")


def analyze_header(data):
    """Analyse le header d'une trame"""
    if len(data) < 2:
        return "Données insuffisantes"

    header = data[:2]
    if header == HEADER_PAC_OUT:
        return "PAC → Passerelle (FA FD)"
    elif header == HEADER_GW_IN:
        return "Passerelle → PAC (FD FA)"
    elif header == HEADER_PAC_RESP:
        return "Réponse PAC (FF FD)"
    else:
        return f"Header inconnu: {header.hex()}"


def decode_temperature(data, offset):
    """Décode une température Little Endian × 100"""
    if offset + 1 >= len(data):
        return None
    value = struct.unpack('<H', data[offset:offset+2])[0]
    if value == 0xFFFF:
        return None
    return value / 100.0


def test_listen_passive(ser, duration=10):
    """
    Test T01: Écoute passive pour détecter les Pings de la PAC
    """
    print(f"\n{'='*60}")
    print("TEST T01: Écoute passive ({} secondes)".format(duration))
    print("Recherche de trames FA FD (Ping PAC)...")
    print('='*60)

    start = time.time()
    buffer = b''
    ping_count = 0

    while time.time() - start < duration:
        chunk = ser.read(100)
        if chunk:
            buffer += chunk
            hex_dump(chunk, f"[{time.time()-start:.1f}s] ")

            # Recherche de Pings
            if HEADER_PAC_OUT in buffer:
                ping_count += 1
                print(f">>> PING détecté ! (#{ping_count})")

    print(f"\nRésultat: {len(buffer)} octets reçus, {ping_count} Pings détectés")
    return buffer, ping_count > 0


def test_pong_response(ser):
    """
    Test T02: Envoi d'un Pong et observation de la réponse
    """
    print(f"\n{'='*60}")
    print("TEST T02: Envoi Pong")
    print('='*60)

    # Vider le buffer
    ser.reset_input_buffer()

    print("Envoi: ", end='')
    hex_dump(PONG, "")
    ser.write(PONG)
    ser.flush()

    time.sleep(2)
    response = ser.read(256)

    print(f"\nRéponse ({len(response)} octets):")
    if response:
        hex_dump(response)
        print(f"Type: {analyze_header(response)}")
    else:
        print("Aucune réponse")

    return response


def test_init_standard(ser):
    """
    Test T03: Envoi de la trame d'initialisation (mode standard)
    """
    print(f"\n{'='*60}")
    print("TEST T03: Initialisation mode standard")
    print('='*60)

    ser.reset_input_buffer()

    print("Envoi: ", end='')
    hex_dump(INIT_STANDARD, "")
    ser.write(INIT_STANDARD)
    ser.flush()

    time.sleep(2)
    response = ser.read(256)

    print(f"\nRéponse ({len(response)} octets):")
    if response:
        hex_dump(response)
        print(f"Type: {analyze_header(response)}")

        # Analyse de la longueur
        if len(response) == 112:
            print(">>> Mode STANDARD détecté (112 octets)")
        elif len(response) == 175:
            print(">>> Mode DEBUG détecté (175 octets)")
    else:
        print("Aucune réponse")

    return response


def test_request_config(ser):
    """
    Test T04: Requête de configuration (Type 0x21)
    """
    print(f"\n{'='*60}")
    print("TEST T04: Requête configuration (Type 0x21)")
    print('='*60)

    ser.reset_input_buffer()

    print("Envoi: ", end='')
    hex_dump(REQ_CONFIG, "")
    ser.write(REQ_CONFIG)
    ser.flush()

    time.sleep(2)
    response = ser.read(256)

    print(f"\nRéponse ({len(response)} octets):")
    if response:
        hex_dump(response)
        print(f"Type: {analyze_header(response)}")

        # Tentative de décodage des températures
        if len(response) >= 10:
            for offset in [4, 6, 8, 10, 12, 14]:
                temp = decode_temperature(response, offset)
                if temp and 0 < temp < 50:
                    print(f"  Offset {offset}: {temp:.2f}°C (potentielle température)")
    else:
        print("Aucune réponse")

    return response


def test_modbus_encapsulated(ser):
    """
    Test T05: Requête Modbus encapsulée
    """
    print(f"\n{'='*60}")
    print("TEST T05: Requête Modbus encapsulée")
    print('='*60)

    ser.reset_input_buffer()

    print("Envoi: ", end='')
    hex_dump(REQ_MODBUS, "")
    ser.write(REQ_MODBUS)
    ser.flush()

    time.sleep(2)
    response = ser.read(256)

    print(f"\nRéponse ({len(response)} octets):")
    if response:
        hex_dump(response)
        print(f"Type: {analyze_header(response)}")
    else:
        print("Aucune réponse")

    return response


def test_compare_1200(ser):
    """
    Test T06: Comparaison avec Modbus standard 1200 bauds
    """
    print(f"\n{'='*60}")
    print("TEST T06: Test Modbus standard (1200 bauds)")
    print('='*60)

    # Reconfigurer en 1200 bauds
    ser.baudrate = 1200
    ser.parity = serial.PARITY_EVEN

    print(f"Reconfiguration: {ser.baudrate} bauds, parité EVEN")

    ser.reset_input_buffer()
    time.sleep(0.5)

    # Requête Modbus standard: lire registre 1 (version firmware)
    # 01 03 00 01 00 01 D5 CA
    request = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA])

    print("Envoi requête Modbus R1: ", end='')
    hex_dump(request, "")
    ser.write(request)
    ser.flush()

    time.sleep(1)
    response = ser.read(50)

    print(f"\nRéponse ({len(response)} octets):")
    if response:
        hex_dump(response)
        if len(response) >= 5 and response[0] == 0x01 and response[1] == 0x03:
            value = (response[3] << 8) | response[4]
            print(f">>> Registre R1 (Firmware): {value}")
    else:
        print("Aucune réponse")

    # Remettre en 115200
    ser.baudrate = BAUDRATE
    ser.parity = PARITY
    print(f"\nRetour à {BAUDRATE} bauds, pas de parité")

    return response


def main():
    # Détection du port
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = find_port()

    if not port:
        print("ERREUR: Aucun port USB trouvé")
        print("Usage: python3 test_usb_boxconnect.py [port]")
        sys.exit(1)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║        Test Protocole USB Box Connect sur RBUV               ║
║        Basé sur les découvertes de @djtef (HACF)             ║
╠══════════════════════════════════════════════════════════════╣
║  Port: {port:<53} ║
║  Baudrate: {BAUDRATE} (Box Connect) / 1200 (Modbus std)       ║
║  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<52} ║
╚══════════════════════════════════════════════════════════════╝
""")

    # Avertissement
    print("ATTENTION: Assurez-vous que pac_aldes_mqtt.py est arrêté !")
    print("  sudo systemctl stop pac_aldes")
    print()

    try:
        # Ouverture du port en 115200
        ser = serial.Serial(
            port=port,
            baudrate=BAUDRATE,
            parity=PARITY,
            stopbits=STOPBITS,
            bytesize=BYTESIZE,
            timeout=TIMEOUT
        )
        print(f"Port {port} ouvert en {BAUDRATE} bauds")

        results = {}

        # T01: Écoute passive
        _, results['T01'] = test_listen_passive(ser, duration=10)

        # T02: Envoi Pong
        results['T02'] = test_pong_response(ser)

        # T03: Initialisation
        results['T03'] = test_init_standard(ser)

        # T04: Requête config
        results['T04'] = test_request_config(ser)

        # T05: Modbus encapsulé
        results['T05'] = test_modbus_encapsulated(ser)

        # T06: Comparaison 1200 bauds
        results['T06'] = test_compare_1200(ser)

        ser.close()

        # Résumé
        print(f"\n{'='*60}")
        print("RÉSUMÉ DES TESTS")
        print('='*60)

        print(f"""
T01 - Écoute passive (Ping):     {'✅ Détecté' if results.get('T01') else '❌ Aucun'}
T02 - Réponse au Pong:           {'✅ Réponse' if results.get('T02') else '❌ Aucune'}
T03 - Initialisation:            {'✅ Réponse' if results.get('T03') else '❌ Aucune'}
T04 - Requête config (0x21):     {'✅ Réponse' if results.get('T04') else '❌ Aucune'}
T05 - Modbus encapsulé:          {'✅ Réponse' if results.get('T05') else '❌ Aucune'}
T06 - Modbus standard 1200:      {'✅ Réponse' if results.get('T06') else '❌ Aucune'}
""")

        # Conclusion
        if results.get('T01') or any(results.get(f'T0{i}') for i in range(2, 6)):
            print(">>> Le RBUV semble supporter le protocole Box Connect !")
            print("    Tests supplémentaires recommandés.")
        elif results.get('T06'):
            print(">>> Le RBUV répond uniquement en Modbus standard (1200 bauds)")
            print("    Le protocole Box Connect ne semble pas supporté.")
        else:
            print(">>> Aucune réponse obtenue. Vérifier les connexions.")

    except serial.SerialException as e:
        print(f"ERREUR série: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrompu par l'utilisateur")
        sys.exit(0)


if __name__ == '__main__':
    main()
