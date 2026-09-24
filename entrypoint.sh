#!/bin/sh
set -e

PWFILE="/mosquitto/config/pwfile"

echo "================================================="
echo "[cremen_mqtt] Starting Mosquitto Broker setup..."
echo "================================================="

# Ensure configuration, data & HTTP www directories exist
mkdir -p /mosquitto/config /mosquitto/data /mosquitto/log /mosquitto/www

# Create a minimal index.html for HTTP health check probes
cat <<'EOF' > /mosquitto/www/index.html
<!DOCTYPE html>
<html>
<head><title>MQTT Broker Active</title></head>
<body><h1>cremen_mqtt Mosquitto Broker is Running</h1></body>
</html>
EOF

# Dynamically generate or update Mosquitto hashed password file
if [ -n "$MQTT_USERNAME" ] && [ -n "$MQTT_PASSWORD" ]; then
    echo "[cremen_mqtt] Configuring user '$MQTT_USERNAME'..."
    mosquitto_passwd -c -b "$PWFILE" "$MQTT_USERNAME" "$MQTT_PASSWORD"
    echo "[cremen_mqtt] Password file generated successfully at $PWFILE."
else
    echo "[cremen_mqtt] WARNING: MQTT_USERNAME or MQTT_PASSWORD environment variable is not set!"
    echo "[cremen_mqtt] Creating empty password file. Authentication will fail until credentials are provided."
    touch "$PWFILE"
fi

# Ensure user 'mosquitto' owns pwfile, www & data dirs, with secure 0700 permissions
chown -R mosquitto:mosquitto /mosquitto/config /mosquitto/data /mosquitto/log /mosquitto/www 2>/dev/null || true
chmod 0700 "$PWFILE"

echo "[cremen_mqtt] Launching Mosquitto MQTT Broker..."
exec mosquitto -c /mosquitto/config/mosquitto.conf
