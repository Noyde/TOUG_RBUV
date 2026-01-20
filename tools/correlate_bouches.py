#!/usr/bin/env python3
"""
Script de correlation bitmap bouches RS485 vs registres USB Modbus

Tourne sur Pi 2B:
1. Sniffe le bus RS485 pour obtenir le bitmap des bouches
2. Quand le bitmap change, SSH vers Pi Zero pour lire les registres USB
3. Compare et affiche les correlations

Usage:
    python3 correlate_bouches.py --pi-zero noyde@192.168.0.43
    python3 correlate_bouches.py --pi-zero noyde@192.168.0.43 --scan 70-90
"""

import serial
import struct
import argparse
import subprocess
import time
import sys

# Configuration RS485 (Pi 2B)
SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 19200
PARITY = 'E'

# Registres a scanner sur Pi Zero
# Plages candidates pour le bitmap des bouches
DEFAULT_REGISTERS = [
    # Registres connus proches
    77, 78, 79, 80, 81, 82, 83, 84, 85,
    # Zone 70-100
    70, 71, 72, 73, 74, 75, 76,
    # Registres TOUG
    5029, 5030, 5031, 5032,
    # Autres candidats
    51, 52, 53, 54, 55,
    90, 91, 92, 93,
    100, 101, 102, 103,
    # Plage 30000 (TOUG)
    30026, 30027, 30028,
]

# Mapping bouches
BOUCHES = {
    0x01: 'K1a',
    0x02: 'K1b',
    0x04: 'K3',
    0x08: 'K4',
    0x10: 'K5',
    0x20: 'K6',
}


def parse_bitmap(byte33):
    """Parse le bitmap des bouches"""
    actives = []
    for mask, name in BOUCHES.items():
        if byte33 & mask:
            actives.append(name)
    return actives


def read_usb_registers(pi_zero_host, registers, port='/dev/ttyACM0'):
    """Lit les registres USB via SSH sur Pi Zero"""
    reg_list = ','.join(str(r) for r in registers)

    cmd = f'''python3 -c "
import minimalmodbus
i = minimalmodbus.Instrument('{port}', 1)
i.serial.baudrate = 1200
i.serial.parity = 'E'
i.serial.timeout = 1
for r in [{reg_list}]:
    try:
        v = i.read_register(r)
        print(f'R{{r}}:{{v}}')
    except:
        print(f'R{{r}}:ERR')
"'''

    try:
        result = subprocess.run(
            ['ssh', '-o', 'ConnectTimeout=5', pi_zero_host, cmd],
            capture_output=True, text=True, timeout=15
        )

        values = {}
        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                parts = line.split(':')
                reg = parts[0]
                val = parts[1] if len(parts) > 1 else 'ERR'
                values[reg] = val
        return values
    except Exception as e:
        return {'error': str(e)}


def sniff_and_correlate(ser, pi_zero_host, registers):
    """Sniffe RS485 et correle avec USB quand bitmap change"""
    buffer = bytearray()
    last_bitmap = None
    last_usb_values = {}

    print(f"Sniff RS485 sur {SERIAL_PORT}")
    print(f"SSH vers {pi_zero_host} quand bitmap change")
    print(f"Registres surveilles: {registers}")
    print("=" * 60)
    print("Ctrl+C pour arreter\n")

    while True:
        # Lire RS485
        chunk = ser.read(256)
        if chunk:
            buffer.extend(chunk)

        # Chercher reponse 80 0b
        while len(buffer) > 133:
            try:
                idx = buffer.index(bytes([0x01, 0x17, 0x80, 0x0b]))
            except ValueError:
                buffer = buffer[-3:]
                break

            if idx + 133 > len(buffer):
                break

            # Extraire bitmap (byte 33)
            bitmap = buffer[idx + 33]
            buffer = buffer[idx + 133:]

            # Si bitmap a change
            if bitmap != last_bitmap:
                timestamp = time.strftime("%H:%M:%S")
                bouches = parse_bitmap(bitmap)
                bouches_str = ','.join(bouches) if bouches else '(aucune)'

                print(f"\n[{timestamp}] CHANGEMENT BITMAP: 0x{bitmap:02X} = {bouches_str}")

                # Lire registres USB
                print(f"  Lecture USB via SSH...")
                usb_values = read_usb_registers(pi_zero_host, registers)

                if 'error' in usb_values:
                    print(f"  ERREUR SSH: {usb_values['error']}")
                else:
                    # Afficher et comparer
                    print(f"  Registres USB:")
                    for reg, val in usb_values.items():
                        old_val = last_usb_values.get(reg, '?')
                        changed = ' <-- CHANGE!' if val != old_val and old_val != '?' else ''
                        print(f"    {reg}: {val}{changed}")

                    # Chercher correlations
                    print(f"\n  Analyse correlation:")
                    for reg, val in usb_values.items():
                        if val != 'ERR':
                            try:
                                v = int(val)
                                if v == bitmap:
                                    print(f"    >>> {reg} = {v} = bitmap 0x{bitmap:02X} MATCH EXACT!")
                                elif v > 0 and v < 64:
                                    # Pourrait etre un bitmap ou index
                                    print(f"    ? {reg} = {v} (0x{v:02X}) - a verifier")
                            except:
                                pass

                    last_usb_values = usb_values

                last_bitmap = bitmap
                print("-" * 60)

        time.sleep(0.01)


def main():
    parser = argparse.ArgumentParser(description='Correlation bitmap RS485 vs USB Modbus')
    parser.add_argument('--pi-zero', required=True,
                        help='SSH host Pi Zero (ex: noyde@192.168.0.43)')
    parser.add_argument('--port', default=SERIAL_PORT,
                        help=f'Port RS485 (defaut: {SERIAL_PORT})')
    parser.add_argument('--scan', default=None,
                        help='Plage registres (ex: 70-90)')
    parser.add_argument('--usb-port', default='/dev/ttyACM0',
                        help='Port USB sur Pi Zero (defaut: /dev/ttyACM0)')

    args = parser.parse_args()

    # Determiner registres a scanner
    registers = DEFAULT_REGISTERS
    if args.scan:
        if '-' in args.scan:
            start, end = map(int, args.scan.split('-'))
            registers = list(range(start, end + 1))
        else:
            registers = [int(r) for r in args.scan.split(',')]

    # Test SSH
    print(f"Test connexion SSH vers {args.pi_zero}...")
    result = subprocess.run(
        ['ssh', '-o', 'ConnectTimeout=5', args.pi_zero, 'echo OK'],
        capture_output=True, text=True, timeout=10
    )
    if 'OK' not in result.stdout:
        print(f"ERREUR: SSH echoue vers {args.pi_zero}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    print("SSH OK!\n")

    try:
        ser = serial.Serial(args.port, BAUDRATE, parity=PARITY, timeout=0.1)
        sniff_and_correlate(ser, args.pi_zero, registers)
    except KeyboardInterrupt:
        print("\nArret.")
    except serial.SerialException as e:
        print(f"Erreur port serie: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
