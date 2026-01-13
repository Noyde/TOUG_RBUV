#pragma once

#include "esphome/core/component.h"
#include "esphome/components/uart/uart.h"

namespace esphome {
namespace aldes_tone {

class AldesToneWriter : public Component {
 public:
  void set_uart(uart::UARTComponent *uart) { this->uart_ = uart; }

  void setup() override {
    ESP_LOGI("aldes_tone", "AldesToneWriter initialisé");
  }

  // Calcul CRC16 Modbus
  uint16_t crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
      crc ^= data[i];
      for (int j = 0; j < 8; j++) {
        if (crc & 0x0001) {
          crc = (crc >> 1) ^ 0xA001;
        } else {
          crc >>= 1;
        }
      }
    }
    return crc;
  }

  // Envoyer une trame 0x17 complète
  // Offsets validés par sniffing télécommande (tests X01-X20, Y01-Y07) - 2025-01-13
  void send_frame(uint16_t niveau, uint16_t boost, uint16_t vacances, uint16_t onoff, uint16_t type_mode) {
    uint8_t frame[74];
    memset(frame, 0, sizeof(frame));

    // En-tête fixe
    frame[0] = 0x01;  // Adresse Modbus
    frame[1] = 0x17;  // Fonction Read/Write Multiple
    frame[2] = 0x00;
    frame[3] = 0x01;  // Sous-code séquence (cycle: 0x01→0x41→0x81→0xC1)
    frame[4] = 0x00;
    frame[5] = 0x40;  // Longueur (64)
    frame[6] = 0x00;
    frame[7] = 0x57;  // Constante
    frame[8] = 0x00;
    frame[9] = 0x1F;  // Constante
    frame[10] = 0x73; // 's'
    frame[11] = 0x70; // 'p' - Signature "sp"
    frame[12] = 0x18;
    frame[13] = 0x04; // Version

    // Offset 14-15: Compteur (incrémente à chaque trame)
    static uint16_t frame_counter = 0;
    frame[14] = (frame_counter >> 8) & 0xFF;
    frame[15] = frame_counter & 0xFF;
    frame_counter++;

    // Offset 18-19: Niveau (0x0000=Confort, 0x00C8=Eco)
    frame[18] = (niveau >> 8) & 0xFF;
    frame[19] = niveau & 0xFF;

    // Offset 20-21: Boost (0x0000=Normal, 0x5678=Boost)
    frame[20] = (boost >> 8) & 0xFF;
    frame[21] = boost & 0xFF;

    // Offset 26-27: Débit nominal (m³/h, ex: 0x0384=900)
    frame[26] = 0x03;
    frame[27] = 0x84;  // 900 m³/h

    // Offset 28-29: PSE nominal (Pa, ex: 0x0017=23)
    frame[28] = 0x00;
    frame[29] = 0x17;  // 23 Pa

    // Offset 30-31: Débit 1 bouche (m³/h, ex: 0x00F0=240)
    frame[30] = 0x00;
    frame[31] = 0xF0;  // 240 m³/h

    // Offset 32-33: PSE mini (Pa, ex: 0x000C=12)
    frame[32] = 0x00;
    frame[33] = 0x0C;  // 12 Pa

    // Offset 34-35: Vacances (0x0000=Off, 0x1234=On)
    frame[34] = (vacances >> 8) & 0xFF;
    frame[35] = vacances & 0xFF;

    // Offset 36-37: On/Off (0x0002=Off, 0x0003=On)
    frame[36] = (onoff >> 8) & 0xFF;
    frame[37] = onoff & 0xFF;

    // Offset 38-39: Type mode (0x000A=Clim, 0x000B=Service, 0x000C=Chauffage)
    frame[38] = (type_mode >> 8) & 0xFF;
    frame[39] = type_mode & 0xFF;

    // Offsets 40-69: Consignes zones (0x7FFE = pas de changement)
    for (int i = 40; i < 70; i += 2) {
      frame[i] = 0x7F;
      frame[i + 1] = 0xFE;
    }

    // Calcul et ajout CRC16 Modbus
    uint16_t crc = crc16(frame, 72);
    frame[72] = crc & 0xFF;
    frame[73] = (crc >> 8) & 0xFF;

    // Envoi de la trame
    this->uart_->write_array(frame, sizeof(frame));
    ESP_LOGI("aldes_tone", "Trame 0x17: niveau=0x%04X, boost=0x%04X, vacances=0x%04X, onoff=0x%04X, type=0x%04X",
             niveau, boost, vacances, onoff, type_mode);
  }

  // === MÉTHODES DE CONTRÔLE ===
  // Paramètres send_frame: (niveau, boost, vacances, onoff, type_mode)

  void set_off() {
    // Off: niveau=Confort, boost=Off, vacances=Off, onoff=Off, type=Chauffage
    send_frame(0x0000, 0x0000, 0x0000, 0x0002, 0x000C);
  }

  void set_chauffage_confort() {
    // Chauffage Confort: niveau=Confort, boost=Off, vacances=Off, onoff=On, type=Chauffage
    send_frame(0x0000, 0x0000, 0x0000, 0x0003, 0x000C);
  }

  void set_chauffage_eco() {
    // Chauffage Eco: niveau=Eco, boost=Off, vacances=Off, onoff=On, type=Chauffage
    send_frame(0x00C8, 0x0000, 0x0000, 0x0003, 0x000C);
  }

  void set_clim_confort() {
    // Clim Confort: niveau=Confort, boost=Off, vacances=Off, onoff=On, type=Clim
    send_frame(0x0000, 0x0000, 0x0000, 0x0003, 0x000A);
  }

  void set_clim_boost() {
    // Clim Boost: niveau=Confort, boost=On, vacances=Off, onoff=On, type=Clim
    send_frame(0x0000, 0x5678, 0x0000, 0x0003, 0x000A);
  }

  void set_vacances() {
    // Vacances: niveau=Confort, boost=Off, vacances=On, onoff=On, type=Chauffage
    send_frame(0x0000, 0x0000, 0x1234, 0x0003, 0x000C);
  }

 protected:
  uart::UARTComponent *uart_{nullptr};
};

}  // namespace aldes_tone
}  // namespace esphome
