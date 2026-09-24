# Use official Eclipse Mosquitto image
FROM eclipse-mosquitto:latest

# Copy configuration and entrypoint script
COPY mosquitto.conf /mosquitto/config/mosquitto.conf
COPY entrypoint.sh /entrypoint.sh

# Grant execution permission to entrypoint script and prepare directories
RUN chmod +x /entrypoint.sh && \
    mkdir -p /mosquitto/data /mosquitto/log /mosquitto/config

# Expose standard MQTT TCP port (1883) and WebSockets port (8080)
EXPOSE 1883 8080

# Execute custom entrypoint script on container launch
ENTRYPOINT ["/entrypoint.sh"]
