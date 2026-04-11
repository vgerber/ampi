#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/wifi.env"
ARDUINO_CLI="/home/vincent/Software/arduino-ide/arduino-ide_2.3.4_Linux_64bit/resources/app/lib/backend/resources/arduino-cli"
ARDUINOJSON_INCLUDE="-I/home/vincent/Arduino/libraries/ArduinoJson/src"

if [ ! -f "$ENV_FILE" ]; then
  echo "Error: $ENV_FILE not found."
  exit 1
fi

source "$ENV_FILE"

EXTRA_FLAGS="$ARDUINOJSON_INCLUDE -DWIFI_SSID=\"$WIFI_SSID\" -DWIFI_PASSWORD=\"$WIFI_PASSWORD\""

if [ "${1}" = "--compile-only" ]; then
  "$ARDUINO_CLI" compile \
    --fqbn esp8266:esp8266:nodemcuv2 \
    --build-property "compiler.cpp.extra_flags=$EXTRA_FLAGS" \
    "$SCRIPT_DIR"
else
  "$ARDUINO_CLI" compile --upload \
    --fqbn esp8266:esp8266:nodemcuv2 \
    --port /dev/ttyUSB0 \
    --build-property "compiler.cpp.extra_flags=$EXTRA_FLAGS" \
    "$SCRIPT_DIR"
fi
