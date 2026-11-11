#include <Arduino.h>
#include <NimBLEDevice.h>
#include <atomic>

constexpr int GPS_RX = 20;
constexpr int GPS_TX = 21;
constexpr unsigned long GPS_BAUD = 115200;
constexpr char SERVICE_UUID[] = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E";
constexpr char TX_UUID[] = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E";

HardwareSerial gps(1);
NimBLECharacteristic *rtcmTx;
std::atomic<bool> subscribed{false};
std::atomic<uint16_t> blePayload{20};

class RtcmCallbacks : public NimBLECharacteristicCallbacks {
  void onSubscribe(NimBLECharacteristic *, NimBLEConnInfo &, uint16_t value) override {
    subscribed = (value & 1) != 0;
  }
};

class ServerCallbacks : public NimBLEServerCallbacks {
  void onConnect(NimBLEServer *server, NimBLEConnInfo &info) override {
    blePayload = info.getMTU() - 3;
    server->updateConnParams(info.getConnHandle(), 12, 12, 0, 400);
  }
  void onMTUChange(uint16_t mtu, NimBLEConnInfo &) override {
    blePayload = mtu - 3;
    Serial.printf("BLE MTU: %u\n", mtu);
  }
  void onDisconnect(NimBLEServer *, NimBLEConnInfo &, int reason) override {
    subscribed = false;
    blePayload = 20;
    Serial.printf("BLE disconnected: %d\n", reason);
  }
};

RtcmCallbacks rtcmCallbacks;
ServerCallbacks serverCallbacks;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Booting");
  gps.setRxBufferSize(8192);
  gps.begin(GPS_BAUD, SERIAL_8N1, GPS_RX, GPS_TX);
  delay(3000);

  const char *commands[] = {
    "UNLOG",
    "MODE BASE TIME 60",
    "RTCM1006 10",
    "RTCM1033 10",
    "RTCM1074 1",
    "RTCM1084 1",
    "RTCM1094 1",
    "RTCM1124 1",
    "RTCM1230 10"
  };
  

  for (const char *command : commands) {
    gps.print(command);
    gps.print("\r\n");
    delay(100);
  }

  NimBLEDevice::init("UM980-RTK");
  NimBLEDevice::setMTU(247);
  auto *server = NimBLEDevice::createServer();
  server->setCallbacks(&serverCallbacks, false);
  server->advertiseOnDisconnect(true);

  auto *service = server->createService(SERVICE_UUID);
  rtcmTx = service->createCharacteristic(TX_UUID, NIMBLE_PROPERTY::NOTIFY);
  rtcmTx->setCallbacks(&rtcmCallbacks);
  service->start();

  auto *advertising = NimBLEDevice::getAdvertising();
  advertising->addServiceUUID(SERVICE_UUID);
  advertising->setName("UM980-RTK");
  advertising->enableScanResponse(true);
  bool started = advertising->start();
  Serial.printf("BLE advertising started: %s\n", started ? "yes" : "no");
}


void loop() {
  static uint8_t chunk[244];
  static size_t length = 0;
  static uint32_t started = 0;

  if (!subscribed) {
    length = 0;
    while (gps.available()) gps.read();
    delay(1);
    return;
  }

  size_t limit = blePayload.load();
  if (limit > sizeof(chunk)) limit = sizeof(chunk);

  while (length < limit && gps.available()) {
    int byte = gps.read();
    if (byte >= 0) {
      if (length == 0) started = millis();
      chunk[length++] = static_cast<uint8_t>(byte);
    }
  }

  if (length && (length >= limit || millis() - started >= 10)) {
    if (rtcmTx->notify(chunk, length)) length = 0;
  }

  delay(1);
}