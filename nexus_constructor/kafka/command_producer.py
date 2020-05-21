import logging
import confluent_kafka
from nexus_constructor.kafka.kafka_interface import KafkaInterface


class CommandProducer(KafkaInterface):
    def __init__(self, address, topic):
        super().__init__()
        self._topic = topic
        configs = {"bootstrap.servers": address, "message.max.bytes": "100000000"}
        self._producer = confluent_kafka.Producer(configs)
        self._poll_thread.start()

    def _poll_loop(self):
        try:
            self._producer.list_topics()
        except confluent_kafka.KafkaException:
            self.connected = False
            return
        else:
            self.connected = True

        while not self._cancelled:
            self._producer.poll(0.5)

    def send_command(self, payload: bytes):
        def ack(err, msg):
            if err:
                logging.debug(f"Message failed delivery: {err}")
            else:
                logging.debug(
                    f"Message delivered to {msg.topic()} {msg.partition()} @ {msg.offset()}"
                )

        self._producer.produce(self._topic, payload, on_delivery=ack)
        self._producer.poll(0)
