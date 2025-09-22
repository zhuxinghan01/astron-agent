import os

from confluent_kafka import Producer
from loguru import logger

from common.service.base import Service, ServiceType


class KafkaProducerService(Service):
    name = ServiceType.KAFKA_PRODUCER_SERVICE

    def __init__(self, config: dict):
        """
        Kafka 生产者服务封装
        :param config: Kafka 配置
        """
        self.config = config
        self.producer = Producer(**config)

    def send(
        self,
        topic: str,
        value: str,
        callback=None,
        timeout: int = int(os.getenv("KAFKA_TIMEOUT", 10)),
    ):
        """
        发送 Kafka 消息
        :param topic: Kafka topic
        :param value: 消息内容（已序列化的 JSON 字符串）
        :param callback: 回调函数
        :param timeout: poll timeout (秒)
        """
        if not callback:
            callback = self._delivery_report
        try:
            self.producer.produce(topic=topic, value=value, callback=callback)
            self.producer.poll(timeout)
        except Exception as e:
            logger.error(f"Kafka message send failed: {e}")
            raise e

    def _delivery_report(self, err, msg):
        """
        消息发送回调函数
        :param err:
        :param msg:
        :return:
        """
        if err is not None:
            logger.error("Message delivery failed: {}".format(err))
        else:
            logger.info(
                "Message delivered to {} [{}]".format(msg.topic(), msg.partition())
            )
