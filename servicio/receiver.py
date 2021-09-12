from kombu.mixins import ConsumerMixin, ConsumerProducerMixin
from kombu import Exchange, Connection, Producer, Consumer, Queue
import sys

exchange = Exchange('logs', type='fanout')
queue = Queue(f'queue.{sys.argv[-1]}', routing_key='', exchange=exchange)


class Receiver(ConsumerProducerMixin):

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(queues=[queue], callbacks=[self.on_message], accept={'application/json'},
                     prefetch_count=1,
                     )]

    def on_message(self, body, message):
        print('RECEIVED MESSAGE: {0!r}'.format(body))

        self.producer.publish(
            {'result': f'Hello {sys.argv[-1]}'},
            exchange='',
            routing_key=message.properties['reply_to'],
            correlation_id=message.properties['correlation_id']
        )

        message.ack()


def main(broker_url):
    connection = Connection(broker_url)
    print(' [x] Awaiting messages')
    worker = Receiver(connection)
    worker.run()


if __name__ == '__main__':
    main('amqp://guest:guest@localhost:5672//')
