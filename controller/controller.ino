#include <ESP8266WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ESP8266mDNS.h>
#include <ArduinoJson.h>

#ifndef WIFI_SSID
#  define WIFI_SSID "ampi-pi"
#endif
#ifndef WIFI_PASSWORD
#  define WIFI_PASSWORD "123"
#endif

const char* ssid     = WIFI_SSID;
const char* password = WIFI_PASSWORD;

const int LED_RED = 2;
const int LED_YELLOW = 0;
const int LED_GREEN = 4;
const int BUZZER = 5;

const int LED_STATUS = 14;

unsigned long led_status_set_time_ms = 0;

int led_red_value = 0;
int led_yellow_value = 0;
int led_green_value = 0;
int buzzer_value = 0;

AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

void connect_wifi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting to ");
  Serial.print(ssid); Serial.println(" ...");

  int connection_attempt = 0;
  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(LED_STATUS, 1);
    delay(100);
    Serial.print(++connection_attempt); Serial.print(' ');
    digitalWrite(LED_STATUS, 0);
    delay(1000);
  }

  Serial.println();
  Serial.println("Connection established!");
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());

  for (int i = 0; i < 5; i++) {
    digitalWrite(LED_STATUS, 1);
    delay(100);
    digitalWrite(LED_STATUS, 0);
    delay(100);
  }
}

String buildStateJson() {
  JsonDocument doc;
  doc["red"] = led_red_value;
  doc["yellow"] = led_yellow_value;
  doc["green"] = led_green_value;
  doc["buzzer"] = buzzer_value;
  doc["signal"] = WiFi.RSSI();
  String buf;
  serializeJson(doc, buf);
  return buf;
}

void broadcastState() {
  ws.textAll(buildStateJson());
  digitalWrite(LED_STATUS, 1);
  led_status_set_time_ms = millis();
}

void applyState(JsonObject& obj) {
  if (obj.containsKey("red")) {
    led_red_value = constrain(obj["red"].as<int>(), 0, 255);
    analogWrite(LED_RED, led_red_value);
  }
  if (obj.containsKey("yellow")) {
    led_yellow_value = constrain(obj["yellow"].as<int>(), 0, 255);
    analogWrite(LED_YELLOW, led_yellow_value);
  }
  if (obj.containsKey("green")) {
    led_green_value = constrain(obj["green"].as<int>(), 0, 255);
    analogWrite(LED_GREEN, led_green_value);
  }
  if (obj.containsKey("buzzer")) {
    buzzer_value = obj["buzzer"].as<int>() ? 1 : 0;
    digitalWrite(BUZZER, buzzer_value);
  }
}

void onWsEvent(AsyncWebSocket* server, AsyncWebSocketClient* client,
               AwsEventType type, void* arg, uint8_t* data, size_t len) {
  if (type == WS_EVT_CONNECT) {
    Serial.printf("WS client #%u connected from %s\n", client->id(),
                  client->remoteIP().toString().c_str());
    client->text(buildStateJson());
  } else if (type == WS_EVT_DISCONNECT) {
    Serial.printf("WS client #%u disconnected\n", client->id());
  } else if (type == WS_EVT_DATA) {
    AwsFrameInfo* info = (AwsFrameInfo*)arg;
    if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
      JsonDocument doc;
      DeserializationError error = deserializeJson(doc, data, len);
      if (error) {
        Serial.print(F("WS JSON parse error: "));
        Serial.println(error.c_str());
        client->text("{\"error\":\"invalid json\"}");
        return;
      }
      JsonObject obj = doc.as<JsonObject>();
      applyState(obj);
      broadcastState();
    }
  }
}

void setup() {
  Serial.begin(115200);         // Start the Serial communication to send messages to the computer
  delay(10);
  Serial.println('\n');
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  pinMode(LED_STATUS, OUTPUT);
  analogWriteRange(255);
  analogWriteFreq(1000);
  analogWrite(LED_RED, 0);
  analogWrite(LED_YELLOW, 0);
  analogWrite(LED_GREEN, 0);
  digitalWrite(LED_STATUS, 1);
  delay(100);
  digitalWrite(LED_STATUS, 0);

  connect_wifi();

  ws.onEvent(onWsEvent);
  server.addHandler(&ws);

  server.on("/ampi", HTTP_GET, [](AsyncWebServerRequest* req) {
    req->send(200, "text/plain", "ampi-client");
  });
  server.on("/name", HTTP_GET, [](AsyncWebServerRequest* req) {
    req->send(200, "text/plain", "vgerber");
  });
  server.onNotFound([](AsyncWebServerRequest* req) {
    req->send(404, "text/plain", "404: Not found");
  });

  server.begin();                           // Actually start the server
  Serial.println("HTTP+WS server started");
}

void handle_wifi_reconnect() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }
  Serial.println("WiFi lost, reconnecting...");
  WiFi.disconnect();
  connect_wifi();
}

void handle_led_status() {
  if (!digitalRead(LED_STATUS)) {
    return;
  }
  if ((millis() - led_status_set_time_ms) > 100) {
    digitalWrite(LED_STATUS, 0);
  }
}

void loop(void) {
  handle_wifi_reconnect();
  ws.cleanupClients();                      // Free memory from disconnected clients
  handle_led_status();
}