import json
import logging
import time
from threading import Thread

import pika
from django.conf import settings
from netaddr import EUI
from rest_framework import serializers

from core.models import Client
from integration.serializers import MessageSerializer


# TODO: make better error resolving instead of this 5hit

def run_consumer():
    try:
        t = Thread(target=start_consumer, args=(settings.RABBITMQ_EVENT_QUEUE,))
        t.start()
    except Exception as e:
        print("\nExiting consumer script with error %s" % e.__repr__())
        exit(1)


def start_consumer(queue):
    restart_counter = 0
    error = ''
    while restart_counter < 10:
        try:
            consumer = RabbitConsumer(rabbit_server_addr=settings.RABBITMQ_HOST,
                                      rabbit_server_port=settings.RABBITMQ_PORT)
            _start_consumer(consumer, queue)
        except Exception as e:
            error = e
            restart_counter += 1
            logging.warning("Restarting worker thread %i time on error %s", restart_counter, error)
            time.sleep(3)
    logging.exception("Exit worker thread with error %s", error)
    exit(1)


def _start_consumer(consumer, queue):
    consumer.channel_in.basic_consume(queue, consumer.callback)
    consumer.channel_in.start_consuming()


def validate_mac(value):
    try:
        return EUI(value)
    except Exception as e:
        raise serializers.ValidationError(e)


class RabbitConsumer:
    def __init__(self, rabbit_server_addr, rabbit_server_port):
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        connection_params = pika.ConnectionParameters(host=rabbit_server_addr, port=rabbit_server_port,
                                                      virtual_host=settings.RABBITMQ_VIRTUAL_HOST,
                                                      credentials=credentials)
        try:
            connection = pika.BlockingConnection(connection_params)
            self.channel_in = connection.channel()

            self.channel_in.queue_declare(queue=settings.RABBITMQ_EVENT_QUEUE, durable=True)
            self.channel_in.queue_bind(exchange=settings.RABBITMQ_EVENT_EXCHANGE,
                                       queue=settings.RABBITMQ_EVENT_QUEUE,
                                       routing_key=settings.RABBITMQ_EVENT_QUEUE_ROUTING_KEY)
            self.channel_in.queue_declare(queue=settings.RABBITMQ_EVENT_DEAD_LETTER_QUEUE, durable=True)
            self.channel_in.queue_bind(exchange=settings.RABBITMQ_EVENT_EXCHANGE,
                                       queue=settings.RABBITMQ_EVENT_DEAD_LETTER_QUEUE,
                                       routing_key=settings.RABBITMQ_EVENT_DEAD_LETTER_QUEUE_ROUTING_KEY)
        except Exception as e:
            print(e)
            raise e

    # Document received message
    def callback(self, ch, method, properties, body):
        try:
            data = json.loads(body)
            instance = Client.objects.get_or_create(mac=validate_mac(data.get("MacAdress")))[0]
            serializer = MessageSerializer(instance=instance, data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        except:
            import traceback
            self.channel_in.basic_publish(exchange=settings.RABBITMQ_EVENT_EXCHANGE,
                                          routing_key=settings.RABBITMQ_EVENT_DEAD_LETTER_QUEUE,
                                          body=body,
                                          properties=pika.BasicProperties(
                                              headers={'traceback': traceback.format_exc()}  # Add a key/value header
                                          ),
                                          )
        ch.basic_ack(delivery_tag=method.delivery_tag)
