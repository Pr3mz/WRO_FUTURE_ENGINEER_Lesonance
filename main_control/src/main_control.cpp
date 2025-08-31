#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <IROVER.h>

// ---- Wi-Fi SoftAP (ESP32 acts as hotspot) ----
const char* AP_SSID = "ESP32-CAR";
const char* AP_PASS = "drive123";        // change if you want

// ---- UDP ----
WiFiUDP udp;
const uint16_t UDP_PORT = 4210;
char rxBuf[64];

// ---- Motor Speed ----
int MOTOR_SPEED = 100;
void setup() {
  Serial.begin(115200);
  ao();

  // Start SoftAP
  WiFi.mode(WIFI_AP);
  bool ok = WiFi.softAP(AP_SSID, AP_PASS);
  Serial.println(ok ? "AP up" : "AP failed");
  Serial.print("AP IP: "); Serial.println(WiFi.softAPIP()); // usually 192.168.4.1

  // Start UDP
  udp.begin(UDP_PORT);
  Serial.print("Listening UDP on port "); Serial.println(UDP_PORT);
}

void loop() {
  int pktSize = udp.parsePacket();
  if (pktSize > 0) {
    IPAddress remote = udp.remoteIP();
    unsigned int remotePort = udp.remotePort();

    int n = udp.read(rxBuf, sizeof(rxBuf) - 1);
    rxBuf[n] = 0;
    String cmd = String(rxBuf);
    cmd.trim();
    cmd.toUpperCase();

    Serial.print("From ");
    Serial.print(remote);
    Serial.print(':');
    Serial.print(remotePort);
    Serial.print("  CMD: ");
    Serial.println(cmd);

    // ACK back so Python can detect comms health
    udp.beginPacket(remote, remotePort);
    udp.write((const uint8_t*)"ACK", 3);
    udp.endPacket();

    // speed set: "SPD120"
    if (cmd.startsWith("SPD")) {
      int newspd = cmd.substring(3).toInt();
      MOTOR_SPEED = constrain(newspd, 0, 255);
      Serial.print("Speed set to "); Serial.println(MOTOR_SPEED);
      return;
    }

    if (cmd == "FWD")        fd(MOTOR_SPEED);
    else if (cmd == "BACK")  bk(MOTOR_SPEED);
    else if (cmd == "LEFT")  tl(MOTOR_SPEED);
    else if (cmd == "RIGHT") tr(MOTOR_SPEED);
    else if (cmd == "STOP")  ao();
    else                     { Serial.println("Unknown cmd => STOP"); ao(); }
  }
}
