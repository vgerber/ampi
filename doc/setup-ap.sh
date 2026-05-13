#!/usr/bin/env bash
# Sets up a NetworkManager Wi-Fi hotspot for ampi and installs a dispatcher
# script that recreates it automatically whenever the wireless interface comes up.
#
# Usage: sudo bash setup-ap.sh [--interface <iface>]
#   --interface   Wireless interface to use (default: auto-detected)
#
# Reads SSID/password from ../controller/wifi.env if present; otherwise falls
# back to the defaults below.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../controller/wifi.env"

# Defaults (overridden by wifi.env)
WIFI_SSID="ampi-pi"
WIFI_PASSWORD="weL0veAMP1"
CON_NAME="ampi-ap"
DISPATCHER_FILE="/etc/NetworkManager/dispatcher.d/99-ampi-hotspot"

# Load credentials from wifi.env if available
if [[ -f "$ENV_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    echo "Loaded credentials from $ENV_FILE"
fi

# Resolve interface
IFACE=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --interface) IFACE="$2"; shift 2 ;;
        *) echo "Unknown argument: $1"; exit 1 ;;
    esac
done

if [[ -z "$IFACE" ]]; then
    # Prefer TP-Link USB dongles (interface names starting with "wlx")
    IFACE=$(nmcli -t -f TYPE,DEVICE device \
        | awk -F: '$1=="wifi" && $2~/^wlx/{print $2; exit}')
fi

if [[ -z "$IFACE" ]]; then
    # Fall back to any wifi interface
    IFACE=$(nmcli -t -f TYPE,DEVICE device \
        | awk -F: '$1=="wifi"{print $2; exit}')
fi

if [[ -z "$IFACE" ]]; then
    echo "Error: no wireless interface found. Specify one with --interface <iface>."
    exit 1
fi

echo "Using interface: $IFACE"

# Create / update the hotspot connection
if nmcli connection show "$CON_NAME" &>/dev/null; then
    echo "Connection '$CON_NAME' already exists – updating…"
    nmcli connection delete "$CON_NAME"
fi

nmcli connection add \
    type wifi \
    ifname "$IFACE" \
    con-name "$CON_NAME" \
    ssid "$WIFI_SSID" \
    mode ap \
    ipv4.method shared \
    wifi-sec.key-mgmt wpa-psk \
    wifi-sec.psk "$WIFI_PASSWORD" \
    connection.autoconnect yes \
    connection.autoconnect-priority 10

echo "Hotspot connection '$CON_NAME' created."

# Bring up the hotspot now
nmcli connection up "$CON_NAME"
echo "Hotspot is up."

# Install dispatcher script
cat > "$DISPATCHER_FILE" <<DISPATCHER
#!/usr/bin/env bash
# Recreates the ampi hotspot whenever the wireless interface comes up.
IFACE="\$1"
ACTION="\$2"

# Only act on the correct interface
[[ "\$IFACE" == "$IFACE" ]] || exit 0

if [[ "\$ACTION" == "up" ]]; then
    # Give NetworkManager a moment to settle
    sleep 2
    if ! nmcli -t -f NAME connection show --active | grep -qx "$CON_NAME"; then
        nmcli connection up "$CON_NAME" &>/dev/null &
    fi
fi
DISPATCHER

chmod 755 "$DISPATCHER_FILE"
echo "Dispatcher installed at $DISPATCHER_FILE"

echo ""
echo "Done. The hotspot '$WIFI_SSID' will be recreated automatically each time"
echo "the $IFACE interface comes back up (wake from sleep, undock, etc.)."
