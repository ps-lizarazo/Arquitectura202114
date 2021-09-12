from kombu import Exchange, Connection, Producer, uuid, Queue

exchange = Exchange('logs', type='fanout')
correlation_id = uuid()
callback_queue = Queue('reply')


def callback_handler(body, message):
    print(f'{body} + { message.properties["correlation_id"]  }')

    message.ack()

with Connection('amqp://guest:guest@localhost:5672//') as conn:
    with conn.channel() as channel:
        producer = Producer(channel)

        producer.publish(
            {'hello': 'world'}, # message to send
            exchange=exchange, # destination exchange
            routing_key='', # destination routing key,
            declare=[exchange], # make sure exchange is declared,
            reply_to=callback_queue.name,
            correlation_id=correlation_id,
            retry=True,
        )
        with conn.Consumer([callback_queue],
                         callbacks=[callback_handler]) as consumer:
            while True:
                conn.drain_events()


        

