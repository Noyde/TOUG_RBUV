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
  void send_frame(uint16_t niveau, uint16_t vacances, uint16_t onoff, uint16_t type_mode) {
    uint8_t frame[74];
    memset(frame, 0, sizeof(frame));

    // En-tête fixe
    frame[0] = 0x01;  // Adresse Modbus
    frame[1] = 0x17;  // Fonction Read/Write Multiple
    frame[2] = 0x00;
    frame[3] = 0x41;  // Sous-code séquence
    frame[4] = 0x00;
    frame[5] = 0x40;  // Longueur
    frame[6] = 0x00;
    frame[7] = 0x57;  // Constante
    frame[8] = 0x00;
    frame[9] = 0x1F;  // Constante
    frame[10] = 0x73; // 's'
    frame[11] = 0x70; // 'p' - Signature "sp"
    frame[12] = 0x18;
    frame[13] = 0x04; // Version

    // Offset 18-19: Niveau (Eco/Confort/Boost)
    frame[18] = (niveau >> 8) & 0xFF;
    frame[19] = niveau & 0xFF;

    // Offset 28-29: Débit nominal (valeur par défaut)
    frame[28] = 0x03;
    frame[29] = 0x84;  // 900 m3/h

    // Offset 30-31: PSE débit nominal
    frame[30] = 0x00;
    frame[31] = 0x17;  // 23 Pa

    // Offset 32-33: Vacances
    frame[32] = (vacances >> 8) & 0xFF;
    frame[33] = vacances & 0xFF;

    // Offset 34-35: On/Off
    frame[34] = (onoff >> 8) & 0xFF;
    frame[35] = onoff & 0xFF;

    // Offset 36-37: Type mode (Chauffage/Clim)
    frame[36] = (type_mode >> 8) & 0xFF;
    frame[37] = type_mode & 0xFF;

    // Pattern fixe offsets 40-69 (consignes non modifiables)
    frame[40] = 0x7F;
    frame[41] = 0xFE;
    for (int i = 42; i < 70; i += 2) {
      frame[i] = 0x7F;
      frame[i + 1] = 0xFE;
    }

    // Calcul et ajout CRC
    uint16_t crc = crc16(frame, 72);
    frame[72] = crc & 0xFF;
    frame[73] = (crc >> 8) & 0xFF;

    // Envoi de la trame
    this->uart_->write_array(frame, sizeof(frame));
    ESP_LOGI("aldes_tone", "Trame envoyée: niveau=0x%04X, vacances=0x%04X, onoff=0x%04X, type=0x%04X",
             niveau, vacances, onoff, type_mode);
  }

  // === MÉTHODES DE CONTRÔLE ===

  void set_off() {
    // Off: niveau=Confort, vacances=Off, onoff=Off, type=Chauffage
    send_frame(0x0000, 0x0000, 0x0002, 0x000C);
  }

  void set_chauffage_confort() {
    send_frame(0x0000, 0x0000, 0x0003, 0x000C);
  }

  void set_chauffage_eco() {
    send_frame(0x00C8, 0x0000, 0x0003, 0x000C);
  }

  void set_clim_confort() {
    send_frame(0x0000, 0x0000, 0x0003, 0x000A);
  }

  void set_clim_boost() {
    send_frame(0x5678, 0x0000, 0x0003, 0x000A);
  }

  void set_vacances() {
    send_frame(0x0000, 0x1234, 0x0003, 0x000C);
  }

 protected:
  uart::UARTComponent *uart_{nullptr};
};

}  // namespace aldes_tone
}  // namespace esphome
