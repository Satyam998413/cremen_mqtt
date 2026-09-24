#!/usr/bin/env python3
"""
Verification client script for testing Mosquitto MQTT Broker on Render.

Usage:
  # Test via WebSockets (WSS for Render deployed service):
  python test_client.py --host cremen-mqtt.onrender.com --port 443 --transport websockets --ssl --user admin --password secret

  # Test locally via WebSockets (WS):
  python test_client.py --host localhost --port 8080 --transport websockets --user admin --password secret

  # Test locally via standard TCP:
  python test_client.py --host localhost --port 1883 --transport tcp --user admin --password secret
"""

import argparse
import sys
import time
import paho.mqtt.client as mqtt

# Topic definitions for test
TEST_TOPIC = "smartcafe/test/status"
TEST_MESSAGE = "Hello from Smart Cafe Verification Client!"

received_messages = []

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✓ Connected successfully to MQTT broker.")
        client.subscribe(TEST_TOPIC)
        print(f"✓ Subscribed to topic: '{TEST_TOPIC}'")
    else:
        print(f"✗ Connection failed with return code: {rc}")
        sys.exit(1)

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"✓ Received message on '{msg.topic}': {payload}")
    received_messages.append(payload)

def main():
    parser = argparse.ArgumentParser(description="Test connection to Mosquitto MQTT broker.")
    parser.add_argument("--host", default="localhost", help="Broker host address")
    parser.add_argument("--port", type=int, default=8080, help="Broker port (443 for HTTPS/WSS on Render, 8080 local WS, 1883 TCP)")
    parser.add_argument("--transport", default="websockets", choices=["websockets", "tcp"], help="Transport protocol")
    parser.add_argument("--path", default="/mqtt", help="WebSocket path (default: /mqtt)")
    parser.add_argument("--ssl", action="store_true", help="Enable SSL/TLS (required for WSS on Render)")
    parser.add_argument("--user", required=True, help="MQTT Username")
    parser.add_argument("--password", required=True, help="MQTT Password")
    args = parser.parse_args()

    print(f"Connecting to broker at {args.host}:{args.port} using {args.transport.upper()}...")

    client_id = f"verification_client_{int(time.time())}"
    
    # Initialize paho-mqtt client with protocol version
    if args.transport == "websockets":
        client = mqtt.Client(client_id=client_id, transport="websockets")
        client.ws_set_options(path=args.path)
    else:
        client = mqtt.Client(client_id=client_id, transport="tcp")

    if args.ssl:
        client.tls_set()

    client.username_pw_set(args.user, args.password)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(args.host, args.port, keepalive=60)
        client.loop_start()

        # Allow time to establish connection
        time.sleep(2)

        print(f"Publishing test message to topic '{TEST_TOPIC}'...")
        client.publish(TEST_TOPIC, TEST_MESSAGE, qos=1)

        # Wait to receive published message
        wait_time = 0
        while len(received_messages) == 0 and wait_time < 5:
            time.sleep(0.5)
            wait_time += 0.5

        if len(received_messages) > 0 and received_messages[0] == TEST_MESSAGE:
            print("\n==========================================")
            print(" VERIFICATION SUCCESSFUL: MQTT Broker works!")
            print("==========================================\n")
        else:
            print("\n==========================================")
            print(" VERIFICATION FAILED: Did not receive expected payload.")
            print("==========================================\n")
            sys.exit(1)

    except Exception as e:
        print(f"✗ Exception occurred during verification: {e}")
        sys.exit(1)
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
