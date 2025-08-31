#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <IROVER.h>

// --- Wi-Fi ---
const char* AP_SSID = "ESP32-CAR";
const char* AP_PASS = "drive123";

// --- UDP ---
WiFiUDP udp;
const uint16_t UDP_PORT = 4210;
char rxBuf[64];

// --- Motors ---
int MOTOR_SPEED = 120;
void stop(){
  motor(1,0);
  motor(2,0);
}
// --- IR Sensors for lap counting ---
const int IR_LEFT = 32;
const int IR_RIGHT = 34;
int lap_count = 0;
bool lap_triggered = false;  // prevent multiple counts per line

void setup() {
    init(0x48);       // IROVER init
    stop();
    Serial.begin(115200);

    pinMode(IR_LEFT, INPUT);
    pinMode(IR_RIGHT, INPUT);

    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    Serial.print("AP IP: "); Serial.println(WiFi.softAPIP());

    udp.begin(UDP_PORT);
    Serial.println("UDP ready");
}

void loop() {
    // --- Receive commands from Python ---
    int pktSize = udp.parsePacket();
    if(pktSize > 0){
        int n = udp.read(rxBuf, sizeof(rxBuf)-1);
        rxBuf[n] = 0;
        String cmd = String(rxBuf);
        cmd.trim();
        cmd.toUpperCase();

        Serial.print("CMD: "); Serial.println(cmd);

        udp.beginPacket(udp.remoteIP(), udp.remotePort());
        udp.write((const uint8_t*)"ACK", 3);
        udp.endPacket();

        if(cmd == "FWD") fd(MOTOR_SPEED);
        else if(cmd == "BACK") bk(MOTOR_SPEED);
        else if(cmd == "LEFT") tl(MOTOR_SPEED);
        else if(cmd == "RIGHT") tr(MOTOR_SPEED);
        else if(cmd == "STOP") stop();
    }

    // --- Lap counting with IR sensors ---
    int leftVal = digitalRead(IR_LEFT);
    int rightVal = digitalRead(IR_RIGHT);

    // Both sensors detect the line (active LOW if using reflective IR)
    if(leftVal == LOW && rightVal == LOW && !lap_triggered){
        lap_count++;
        lap_triggered = true;
        Serial.print("Lap completed! Total laps: ");
        Serial.println(lap_count);
    }

    // Reset trigger when sensors are off the line
    if(leftVal == HIGH || rightVal == HIGH){
        lap_triggered = false;
    }

    delay(10);
}
