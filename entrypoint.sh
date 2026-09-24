#!/bin/sh
set -e

PWFILE="/mosquitto/config/pwfile"

echo "================================================="
echo "[cremen_mqtt] Starting Mosquitto Broker setup..."
echo "================================================="

# Ensure configuration & data directories exist
mkdir -p /mosquitto/config /mosquitto/data /mosquitto/log

# Dynamically generate or update Mosquitto hashed password file
if [ -n "$MQTT_USERNAME" ] && [ -n "$MQTT_PASSWORD" ]; then
    echo "[cremen_mqtt] Configuring user '$MQTT_USERNAME'..."
    mosquitto_passwd -c -b "$PWFILE" "$MQTT_USERNAME" "$MQTT_PASSWORD"
    chmod 0600 "$PWFILE"
    echo "[cremen_mqtt] Password file generated successfully at $PWFILE."
else
    echo "[cremen_mqtt] WARNING: MQTT_USERNAME or MQTT_PASSWORD environment variable is not set!"
    echo "[cremen_mqtt] Creating empty password file. Authentication will fail until credentials are provided."
    touch "$PWFILE"
    chmod 0600 "$PWFILE"
fi

echo "[cremen_mqtt] Launching Mosquitto MQTT Broker..."
exec mosquitto -c /mosquitto/config/mosquitto.conf
