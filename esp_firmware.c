#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <ArduinoJson.h>

const char* ssid     = "";         // The SSID (name) of the Wi-Fi network you want to connect to
const char* password = "";     // The password of the Wi-Fi network


const int LED_RED = 2;
const int LED_YELLOW = 0;
const int LED_GREEN = 4;
const int BUZZER = 5;

const int LED_STATUS = 14;

int led_status_set_time_ms = 0;

ESP8266WebServer server(80);


void setCrossOrigin(){
  server.sendHeader(F("Access-Control-Allow-Origin"), F("*"));
  server.sendHeader(F("Access-Control-Max-Age"), F("600"));
  server.sendHeader(F("Access-Control-Allow-Methods"), F("PUT,GET,OPTIONS"));
  server.sendHeader(F("Access-Control-Allow-Headers"), F("*"));
};

void sendCrossOriginHeader(){
  setCrossOrigin();
  server.send(204);
}

void sendState() {
  // Use arduinojson.org/v6/assistant to compute the capacity.
  StaticJsonDocument<96> doc;

  doc["red"] = digitalRead(LED_RED);
  doc["yellow"] = digitalRead(LED_YELLOW);
  doc["green"] = digitalRead(LED_GREEN);
  doc["buzzer"] = digitalRead(BUZZER);
  doc["signal"] = WiFi.RSSI();

  String buf;
  serializeJson(doc, buf);
  setCrossOrigin();
  server.send(200, F("application/json"), buf);
  digitalWrite(LED_STATUS, 1);
  led_status_set_time_ms = millis();
}

void setState() {
  String postBody = server.arg("plain");
  DynamicJsonDocument doc(512);
  DeserializationError error = deserializeJson(doc, postBody);
  if (error) {
        // if the file didn't open, print an error:
    Serial.print(F("Error parsing JSON "));
    Serial.println(error.c_str());
 
    String msg = error.c_str();
    setCrossOrigin();
    server.send(400, F("text/plain"), "Error in parsin json body! " + msg);
    return;
  }

  JsonObject postObj = doc.as<JsonObject>();
  
  if(postObj.containsKey("red")){
    digitalWrite(LED_RED, postObj["red"]);
  }
  if(postObj.containsKey("yellow")){
    digitalWrite(LED_YELLOW, postObj["yellow"]);
  }
  if(postObj.containsKey("green")){
    digitalWrite(LED_GREEN, postObj["green"]);
  }
  if(postObj.containsKey("buzzer")){
    digitalWrite(BUZZER, postObj["buzzer"]);
  }
  sendState();
}

void redirectToStates() {
  server.sendHeader("Location", "/states", true);
  server.send (302, "text/plain", "");
}

void sendMeta() {
  setCrossOrigin();
  server.send (200, "text/plain", "ampi-client");
}

void sendName() {
  setCrossOrigin();
  server.send (200, "text/plain", "vgerber");
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
  digitalWrite(LED_STATUS, 1);
  delay(100);
  digitalWrite(LED_STATUS, 0);
  
  
  WiFi.begin(ssid, password);             // Connect to the network
  Serial.print("Connecting to ");
  Serial.print(ssid); Serial.println(" ...");

  int i = 0;
  while (WiFi.status() != WL_CONNECTED) { // Wait for the Wi-Fi to connect
    digitalWrite(LED_STATUS, 1);
    delay(100);
    Serial.print(++i); Serial.print(' ');
    digitalWrite(LED_STATUS, 0);
    delay(1000);
  }

  for(int i = 0; i < 3; i++) {
    digitalWrite(LED_STATUS, 1);
    delay(100);
    digitalWrite(LED_STATUS, 0);
    delay(100);
  }

  Serial.println('\n');
  Serial.println("Connection established!");  
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());         // Send the IP address of the ESP8266 to the computer

  server.on("/", HTTP_GET, redirectToStates);
  server.on("/ampi", HTTP_GET, sendMeta);
  server.on("/name", HTTP_GET, sendName);
  server.on("/states", HTTP_GET, sendState);
  server.on("/states", HTTP_PUT, setState);
  server.on("/states", HTTP_OPTIONS, sendCrossOriginHeader);
  server.onNotFound(handleNotFound);

  server.begin();                           // Actually start the server
  Serial.println("HTTP server started");
}

void handle_led_status() {
  if(!digitalRead(LED_STATUS)) {
    return;
  }
  if((millis() - led_status_set_time_ms) > 100) {
    digitalWrite(LED_STATUS, 0);
  }
}

void loop(void){
  server.handleClient();                    // Listen for HTTP requests from clients
  handle_led_status();
}

void handleNotFound(){
  server.send(404, "text/plain", "404: Not found"); // Send HTTP status 404 (Not Found) when there's no handler for the URI in the request
}