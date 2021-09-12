from kombu.mixins import ConsumerProducerMixin
from kombu import Exchange, Connection, Queue
import tasks.validar as servicioTasks
import sys

exchange = Exchange('task_validador', type='fanout')

class Receiver(ConsumerProducerMixin):

    def __init__(self, connection, worker_name):
        self.connection = connection
        self.worker_name = worker_name
        self.queue = Queue(f'validador_queue.{self.worker_name}', routing_key='', exchange=exchange)

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(queues=[self.queue], callbacks=[self.on_message], accept={'application/json'},
                     prefetch_count=1,
                     )]

    def on_message(self, body, message):
        print('RECEIVED MESSAGE: {0!r}'.format(body))
        response = {}
        if self.worker_name == 'servicio_tres':
            response['validacion'] = servicioTasks.agendarCitaMedica('fail')
        else:
            response['validacion'] = servicioTasks.agendarCitaMedica()
        
        response['worker_name'] = self.worker_name
        
        self.producer.publish(
            response,
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
