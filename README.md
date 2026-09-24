# cremen_mqtt - Render-hosted Eclipse Mosquitto MQTT Broker

A lightweight, deployment-ready project for hosting an **Eclipse Mosquitto MQTT broker** on **Render** using a custom Docker container. It supports dynamic credentials configured via environment variables without hardcoding passwords into version control.

---

## 🌟 Key Features

- **Dynamic Authentication**: User credentials (`MQTT_USERNAME`, `MQTT_PASSWORD`) are passed as environment variables and converted to Mosquitto's hashed password format at container startup (`entrypoint.sh`).
- **Dual Protocol Support**:
  - **Port 1883**: Standard MQTT TCP Listener.
  - **Port 8080**: MQTT over WebSockets (`protocol websockets`), allowing seamless routing through Render's reverse proxy (`wss://your-app.onrender.com`).
- **Zero Secrets Committed**: Passwords and usernames are kept out of version control and Docker image layers.
- **Render Blueprint Included**: Declarative `render.yaml` infrastructure specification.

---

## 📁 Project Structure

```
cremen_mqtt/
├── Dockerfile           # Multi-stage custom Mosquitto image builder
├── entrypoint.sh        # POSIX script for dynamic credential hashing & process launch
├── mosquitto.conf       # Custom Mosquitto configuration (TCP & WS ports, persistence, auth)
├── render.yaml          # Render Blueprint (Infrastructure-as-Code)
├── test_client.py       # Python verification script (paho-mqtt)
├── test_client.js       # Node.js verification script (mqtt)
└── README.md            # Comprehensive documentation
```

---

## 🚀 Step-by-Step Deployment Guide for Render

### Method 1: Render Blueprints (Recommended)

1. **Push Repository to GitHub**: Ensure `cremen_mqtt/` (or your repo root) contains `render.yaml`, `Dockerfile`, `mosquitto.conf`, and `entrypoint.sh`.
2. **Open Render Dashboard**: Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Blueprint**.
3. **Connect Repository**: Select your GitHub repository.
4. **Configure Environment Variables**:
   - During setup, Render will prompt for un-synchronized variables:
     - `MQTT_USERNAME`: Enter desired username (e.g., `smartcafe_admin`).
     - `MQTT_PASSWORD`: Enter a secure strong password.
5. **Deploy**: Render will build the Docker container and start your Mosquitto broker.

---

### Method 2: Manual Web Service Creation

1. Go to **Render Dashboard** -> **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Choose **Docker** as the environment runtime.
4. Set the build context:
   - **Root Directory**: `cremen_mqtt` (if nested) or `./`
   - **Dockerfile Path**: `./Dockerfile`
5. Under **Environment Variables**, add:
   - `MQTT_USERNAME`: `<your_mqtt_username>`
   - `MQTT_PASSWORD`: `<your_mqtt_password>`
   - `PORT`: `8080` *(tells Render's SSL/TLS proxy to route incoming WebSocket traffic to port 8080 inside the container)*.
6. Click **Create Web Service**.

---

## 🧪 Local Testing & Development

### 1. Build and Run Container Locally

```bash
cd cremen_mqtt

# Build Docker image
docker build -t cremen_mqtt .

# Run container with environment variables
docker run -d \
  --name my_mqtt_broker \
  -p 1883:1883 \
  -p 8080:8080 \
  -e MQTT_USERNAME=admin \
  -e MQTT_PASSWORD=secret \
  cremen_mqtt
```

### 2. Verify Connection using Python Script

```bash
# Install paho-mqtt
pip install paho-mqtt

# Test local WebSockets (Port 8080)
python test_client.py --host localhost --port 8080 --transport websockets --user admin --password secret

# Test local TCP (Port 1883)
python test_client.py --host localhost --port 1883 --transport tcp --user admin --password secret
```

### 3. Verify Deployed Render Service (Secure WebSockets - WSS)

```bash
# Replace with your actual Render service hostname
python test_client.py \
  --host cremen-mqtt.onrender.com \
  --port 443 \
  --transport websockets \
  --ssl \
  --user admin \
  --password secret
```

---

## 📱 Flutter Integration Example (`mqtt_client` package)

In Flutter applications, connect via WebSockets to Render's HTTPS/WSS proxy:

```dart
import 'package:mqtt_client/mqtt_browser_client.dart'; // or mqtt_server_client.dart
import 'package:mqtt_client/mqtt_client.dart';

Future<void> connectMqtt() async {
  final client = MqttBrowserClient('wss://cremen-mqtt.onrender.com/mqtt', 'flutter_client');
  client.port = 443;
  client.keepAlivePeriod = 60;
  client.websocketProtocols = MqttClientConstants.protocolsSingleDefault;

  final connMessage = MqttConnectMessage()
      .authenticateAs('admin', 'secret')
      .withClientIdentifier('flutter_client')
      .startClean();
  
  client.connectionMessage = connMessage;

  try {
    await client.connect();
    print('Connected to Render MQTT broker via WSS!');
  } catch (e) {
    print('Connection error: $e');
  }
}
```

---

## 🔐 Security & Best Practices

- **Never hardcode passwords**: Always rely on environment variables `MQTT_USERNAME` and `MQTT_PASSWORD`.
- **Render WebSockets Security**: Render automatically provides SSL/TLS termination on `wss://your-app.onrender.com`, encrypting all transit traffic without requiring manual SSL certificate setup inside Mosquitto.
