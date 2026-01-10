#!/usr/bin/env python3
"""
TOUG_RBUV - Test écriture Modbus standard (échec attendu)
Vérifie que les fonctions 0x06 et 0x10 retournent bien une erreur.

Usage:
    python3 test_write_modbus.py              # Test sur R9 (mode PAC)
    python3 test_write_modbus.py --register 31100  # Test registre TOUG

Licence: MIT
"""

import argparse
import sys
import time
import serial

# Configuration
SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 1200
MODBUS_ADDRESS = 0x01


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


def test_write_fc06(ser, register, value=4):
    """
    Test écriture FC 0x06 (Write Single Register)
    Résultat attendu sur RBUV: illegal function ou illegal data address
    """
    print(f"\n--- Test FC 0x06 (Write Single Register) ---")
    print(f"    Registre: {register}, Valeur: {value}")

    request = bytes([
        MODBUS_ADDRESS,
        0x06,
        (register >> 8) & 0xFF,
        register & 0xFF,
        (value >> 8) & 0xFF,
        value & 0xFF
    ])
    crc = calculate_crc(request)
    request += bytes([crc & 0xFF, (crc >> 8) & 0xFF])

    print(f"    Trame TX: {request.hex()}")

    ser.reset_input_buffer()
    ser.write(request)
    time.sleep(0.2)

    response = ser.read(8)
    print(f"    Trame RX: {response.hex() if response else '(timeout)'}")

    if len(response) >= 3 and response[1] & 0x80:
        error_code = response[2]
        errors = {1: "illegal function", 2: "illegal data address", 3: "illegal data value"}
        print(f"    ✅ Erreur attendue: {errors.get(error_code, f'0x{error_code:02X}')}")
        return True
    elif len(response) == 0:
        print(f"    ⚠️ Timeout (pas de réponse)")
        return False
    else:
        print(f"    ❌ ATTENTION: Écriture acceptée (inattendu!)")
        return False


def test_write_fc10(ser, register, value=4):
    """
    Test écriture FC 0x10 (Write Multiple Registers)
    Résultat attendu sur RBUV: illegal data address
    """
    print(f"\n--- Test FC 0x10 (Write Multiple Registers) ---")
    print(f"    Registre: {register}, Valeur: {value}")

    request = bytes([
        MODBUS_ADDRESS,
        0x10,
        (register >> 8) & 0xFF,
        register & 0xFF,
        0x00, 0x01,  # Nombre de registres
        0x02,        # Nombre de bytes
        (value >> 8) & 0xFF,
        value & 0xFF
    ])
    crc = calculate_crc(request)
    request += bytes([crc & 0xFF, (crc >> 8) & 0xFF])

    print(f"    Trame TX: {request.hex()}")

    ser.reset_input_buffer()
    ser.write(request)
    time.sleep(0.2)

    response = ser.read(8)
    print(f"    Trame RX: {response.hex() if response else '(timeout)'}")

    if len(response) >= 3 and response[1] & 0x80:
        error_code = response[2]
        errors = {1: "illegal function", 2: "illegal data address", 3: "illegal data value"}
        print(f"    ✅ Erreur attendue: {errors.get(error_code, f'0x{error_code:02X}')}")
        return True
    elif len(response) == 0:
        print(f"    ⚠️ Timeout (pas de réponse)")
        return False
    else:
        print(f"    ❌ ATTENTION: Écriture acceptée (inattendu!)")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test écriture Modbus (échec attendu)")
    parser.add_argument("--port", default=SERIAL_PORT, help="Port série")
    parser.add_argument("--register", "-r", type=int, default=9, help="Registre à tester (défaut: 9)")
    parser.add_argument("--value", "-v", type=int, default=4, help="Valeur à écrire (défaut: 4)")
    args = parser.parse_args()

    print("""
╔══════════════════════════════════════════════════════════════╗
║     TOUG_RBUV - Test Écriture Modbus Standard                ║
║     Résultat attendu: ÉCHEC (illegal function/data address)  ║
╚══════════════════════════════════════════════════════════════╝
    """)

    try:
        ser = serial.Serial(
            port=args.port,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print(f"✅ Port série: {args.port} @ {BAUDRATE} bauds")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

    try:
        fc06_ok = test_write_fc06(ser, args.register, args.value)
        fc10_ok = test_write_fc10(ser, args.register, args.value)

        print(f"\n{'='*60}")
        print(f"  Résumé: FC 0x06 {'✅' if fc06_ok else '❌'} | FC 0x10 {'✅' if fc10_ok else '❌'}")
        print(f"{'='*60}")

    finally:
        ser.close()


if __name__ == "__main__":
    main()
