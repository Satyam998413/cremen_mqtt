/**
 * Verification client script in Node.js for testing Mosquitto MQTT Broker on Render.
 *
 * Requirements:
 *   npm install mqtt
 *
 * Usage:
 *   # WSS on Render:
 *   node test_client.js wss://cremen-mqtt.onrender.com admin secret
 *
 *   # Local WebSockets:
 *   node test_client.js ws://localhost:8080 admin secret
 */

const mqtt = require('mqtt');

const url = process.argv[2] || 'ws://localhost:8080';
const username = process.argv[3] || 'admin';
const password = process.argv[4] || 'secret';

const topic = 'smartcafe/test/status';
const testMessage = 'Hello from Smart Cafe Node.js Client!';

console.log(`Connecting to ${url} as user '${username}'...`);

const client = mqtt.connect(url, {
  username: username,
  password: password,
  clientId: 'node_test_client_' + Math.random().toString(16).substring(2, 8),
  rejectUnauthorized: true,
});

client.on('connect', () => {
  console.log('✓ Connected successfully to MQTT broker.');

  client.subscribe(topic, (err) => {
    if (err) {
      console.error('✗ Subscription failed:', err);
      process.exit(1);
    }
    console.log(`✓ Subscribed to topic: '${topic}'`);

    console.log(`Publishing test message: "${testMessage}"...`);
    client.publish(topic, testMessage, { qos: 1 });
  });
});

client.on('message', (t, message) => {
  const payload = message.toString();
  console.log(`✓ Received message on '${t}': ${payload}`);

  if (payload === testMessage) {
    console.log('\n==========================================');
    console.log(' VERIFICATION SUCCESSFUL: Broker operational!');
    console.log('==========================================\n');
    client.end();
    process.exit(0);
  }
});

client.on('error', (err) => {
  console.error('✗ Connection error:', err.message);
  client.end();
  process.exit(1);
});
