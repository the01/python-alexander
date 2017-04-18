FROM rabbitmq:3

RUN rabbitmq-plugins enable --offline rabbitmq_management
RUN rabbitmq-plugins enable --offline rabbitmq_mqtt

# Expose management
EXPOSE 15672
# Expose mqtt
EXPOSE 1883

ADD rabbitmq.config /etc/rabbitmq/
ADD rabbit_import.json /etc/rabbitmq/
